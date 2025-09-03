"""
This file is the main entry point for running the Pictorus device manager.
It contains the DeviceManager class which orchestrates communication with
external services, and manages applications and targets on the device.
"""

from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from tempfile import TemporaryFile
import threading
import socket
from typing import Callable, Dict, Union

from aiortc import RTCSessionDescription
import requests

from pictorus.comms.comms_handler import CommsConfig, CommsHandler, TelemData
from pictorus.comms.webrtc_comms_handler import RTCOfferData, WebRtcCommsHandler
from pictorus.daemons.utils import get_daemon
from pictorus.comms.mqtt_comms_handler import MqttCommsHandler
from pictorus.date_utils import utc_timestamp_ms
from pictorus.types import DeviceState, LogMessage, NetworkData, TargetState
from . import __version__ as CURRENT_VERSION
from .exceptions import DaemonError, TargetMissingError
from .updates_manager import UpdatesManager
from .config import load_app_manifest, store_app_manifest, Config
from .logging_utils import get_logger
from .command import Command, CmdType, CommandResult, DeployTarget, DeployTargetType, StatusCode
from .target_manager.target_manager import TargetManager, TargetMgrConfig
from .target_manager.proc_target_manager import ProcTargetManager
from .target_manager.embedded_target_manager import EmbeddedTargetManager
from .constants import PICTORUS_SERVICE_NAME

logger = get_logger()
config = Config()


def get_ip():
    ip_addr = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0)
        try:
            sock.connect(("10.254.254.254", 1))
            ip_addr = sock.getsockname()[0]
        except socket.error:
            ip_addr = None

    return ip_addr


class DeviceManager:
    """Main class for managing the Pictorus device and its applications."""

    def __init__(self, version_mgr: UpdatesManager):
        self._version_manager = version_mgr

        self.complete = threading.Event()
        # TODO: It's possible we can't resolve IP address on startup.
        # We should have something that occasionally checks these to see
        # if they have changed and updates the device state accordingly
        self._network_data = NetworkData(
            ip_address=get_ip(),
            hostname=socket.gethostname(),
        )

        self._app_manifest = load_app_manifest()
        targets = [DeployTarget(t) for t in self._app_manifest.get("targets", [])]
        target_states = {
            k: TargetState.from_dict(v)
            for k, v in self._app_manifest.get("target_states", {}).items()
        }
        self._target_managers: Dict[str, TargetManager] = {
            t.id: self._init_target_manager(t, target_state=target_states[t.id], start=False)
            for t in targets
            if t.id in target_states
        }
        self._active_embedded_target: Union[EmbeddedTargetManager, None] = None

        comms_config = CommsConfig(
            process_cmd=self._process_cmd, sync_device_state=self._update_device_state
        )
        self._mqtt_handler = MqttCommsHandler(comms_config)
        self._webrtc_handler = WebRtcCommsHandler(comms_config)
        self._telemetry_heartbeat_time = datetime.now(timezone.utc)

    def __enter__(self):
        self._update_device_state()

        for mgr in self._target_managers.values():
            if isinstance(mgr, ProcTargetManager):
                mgr.open()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.complete.set()

        for mgr in self._target_managers.values():
            mgr.close()

        self._for_each_handler(lambda h: h.close())

    def _for_each_handler(self, cb: Callable[[CommsHandler], None]):
        """Call a function for each communication handler."""
        cb(self._mqtt_handler)
        cb(self._webrtc_handler)

    def _persist_changes(self, desired_state: Union[DeviceState, None] = None):
        self._update_manifest()
        self._update_device_state(desired_state=desired_state)

    def _aggregate_target_states(self) -> Dict[str, Union[TargetState, None]]:
        return {k: v.target_state for k, v in self._target_managers.items() if v.target_state}

    def _update_manifest(self):
        target_data = sorted(
            [v.target.to_dict() for v in self._target_managers.values()], key=lambda x: x["id"]
        )
        manifest = {
            "targets": target_data,
            "target_states": {
                k: asdict(v) if v else None for k, v in self._aggregate_target_states().items()
            },
        }

        store_app_manifest(manifest)
        self._app_manifest = manifest

    def _update_device_state(self, desired_state: Union[DeviceState, None] = None):
        cached_version = self._version_manager.last_installed if self._version_manager else None
        reported_state = DeviceState(
            connected=True,
            target_states=self._aggregate_target_states(),
            version=CURRENT_VERSION,
            cached_version=cached_version,
            network=self._network_data,
        )

        state_data = {"reported": reported_state}
        if desired_state:
            state_data["desired"] = desired_state

        self._for_each_handler(
            lambda handler: handler.update_device_state(
                reported_state=reported_state, desired_state=desired_state
            )
        )

    def _upload_logs(self, cmd: Command):
        upload_data = cmd.data["upload_dest"]
        line_count = str(cmd.data["line_count"])

        with TemporaryFile("wb+") as tmp_log:
            try:
                daemon = get_daemon()
            except DaemonError:
                logger.error("Unable to upload logs: service logs not found")
                return

            logs = daemon.logs(service_name=PICTORUS_SERVICE_NAME, number_of_lines=int(line_count))

            tmp_log.write(logs.encode("utf-8"))
            tmp_log.seek(0)
            tmp_log.flush()

            # TODO: This loads the entire uncompressed log contents into memory.
            # Would be nicer to write to a (possible compressed?) file and then upload in chunks
            # if data exceeds a certain size
            response = requests.post(
                upload_data["url"], data=upload_data["fields"], files={"file": tmp_log}
            )
            response.raise_for_status()

    def _init_target_manager(
        self, target: DeployTarget, target_state: Union[TargetState, None] = None, start=True
    ) -> TargetManager:
        if not target_state:
            target_state = TargetState()

        mgr_class = None
        if target.type == DeployTargetType.PROCESS:
            mgr_class = ProcTargetManager
        elif target.type == DeployTargetType.EMBEDDED:
            mgr_class = EmbeddedTargetManager
        else:
            raise ValueError(f"Unknown target type: {target.type}")

        config = TargetMgrConfig(
            target=target,
            target_state=target_state,
            updates_mgr=self._version_manager,
            sync_device_state_cb=self._update_device_state,
            add_log_cb=self._add_log,
            add_telem_cb=self._add_telemetry,
        )
        mgr = mgr_class(config)

        # This is an intentionally delayed start for the class to initialize until
        # _get_target_manager is called. Note: ProcTargetManager will start immediately
        # and EmbeddedTargetManager will start when commands are dispatched.
        if start:
            mgr.open()

        return mgr

    def _get_target_manager(
        self, cmd: Command, target: Union[DeployTarget, None] = None
    ) -> TargetManager:
        if cmd.target_id is None:
            raise ValueError("Empty target ID specified")

        if cmd.target_id not in self._target_managers:
            if not target:
                raise TargetMissingError(
                    f"Target ID: {cmd.target_id} not found and no target provided for command"
                )

            self._target_managers[target.id] = self._init_target_manager(target)

        target_mgr = self._target_managers[cmd.target_id]
        curr_target = target_mgr.target
        if target is not None and (
            curr_target.type != target.type
            or curr_target.options.get("platform_target") != target.options.get("platform_target")
        ):
            logger.info("Target type has changed. Reinitializing target manager")
            target_mgr.close()
            target_mgr = self._init_target_manager(target)
            self._target_managers[cmd.target_id] = target_mgr

        return self._target_managers[cmd.target_id]

    def _add_log(self, log: LogMessage, target_id: str):
        """Add log entries to the communication handlers."""
        self._for_each_handler(lambda handler: handler.add_log(log, target_id))

    def _add_telemetry(self, data: TelemData):
        """Add telemetry data to the communication handlers and log a heartbeat."""
        self._for_each_handler(lambda handler: handler.add_telemetry(data))
        # Log a heartbeat to show the app is still running, successfully decoding telemetry,
        # and attempting to send it
        if data.utc_time_ms > utc_timestamp_ms(self._telemetry_heartbeat_time):
            logger.info(
                "Heartbeat for successful telemetry decoding for target: %s", data.target_id
            )
            self._telemetry_heartbeat_time = datetime.now(timezone.utc) + timedelta(seconds=60)

    def _process_cmd(
        self, cmd: Command, target: Union[DeployTarget, None]
    ) -> Union[CommandResult, None]:
        desired_changes = DeviceState()
        # Special case here to make sure the desired shadow state reflects the commanded state
        if cmd.type == CmdType.RUN_APP:
            desired_changes.target_states = {
                cmd.target_id: TargetState(run_app=cmd.data["run_app"])
            }

        status = StatusCode.ERROR
        result = None
        try:
            result = self._process_cmd_inner(cmd, target=target)
            status = StatusCode.SUCCESS
        except TargetMissingError:
            logger.warning("Received command for missing target: %s", cmd.target_id)
            # Clear the desired state for the missing target
            # so we don't keep getting change events for it
            if desired_changes.target_states is None:
                desired_changes.target_states = {}

            desired_changes.target_states[cmd.target_id] = None
        except Exception as e:
            logger.error("Error processing local command: %s", e, exc_info=True)
        finally:
            self._persist_changes(desired_state=desired_changes)

        if not cmd.id:
            return None

        return result or CommandResult(id=cmd.id, type=cmd.type, status=status)

    def _process_cmd_inner(
        self, cmd: Command, target: Union[DeployTarget, None]
    ) -> Union[CommandResult, None]:
        logger.info("Received command: %s", cmd)

        if target:
            logger.info("With target: %s", target.to_dict())

        # First handle any commands that aren't target-specific
        if cmd.type == CmdType.UPLOAD_LOGS:
            self._upload_logs(cmd)
            return

        if cmd.type == CmdType.WEBRTC_OFFER:
            if not cmd.id:
                raise ValueError("WebRTC command must have an ID")

            offer = RTCOfferData(
                session_id=cmd.data["session_id"], offer=RTCSessionDescription(**cmd.data["offer"])
            )
            data = self._webrtc_handler.accept_offer(offer)
            return CommandResult(
                id=cmd.id, type=cmd.type, status=StatusCode.SUCCESS, data=asdict(data)
            )

        # Check if there is an active embedded target and compare it to the
        # command target. If they don't match, close the active target, it
        # will be opened in the subsequent _get_target_manager call.
        if self._active_embedded_target:
            mgr = self._target_managers.get(cmd.target_id)
            target_data = target or (mgr.target if mgr else None)
            is_embedded = target_data and target_data.type == DeployTargetType.EMBEDDED
            if is_embedded and cmd.target_id != self._active_embedded_target.target_id:
                self._active_embedded_target.close()
                self._active_embedded_target = None

        mgr = self._get_target_manager(cmd, target=target)
        if isinstance(mgr, EmbeddedTargetManager):
            self._active_embedded_target = mgr

        mgr.handle_command(cmd)
