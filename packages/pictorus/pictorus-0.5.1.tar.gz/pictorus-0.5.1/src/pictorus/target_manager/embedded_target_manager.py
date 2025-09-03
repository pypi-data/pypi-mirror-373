from datetime import datetime, timedelta, timezone
import json
import re
import fnmatch
from concurrent import futures
import threading
from time import sleep
from typing import Optional, Union, cast

from pyocd.core.session import Session
from pyocd.core.helpers import ConnectHelper
from pyocd.target.pack.pack_target import is_pack_target_available
from pyocd.probe.debug_probe import DebugProbe
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.target import TARGET
from pyocd.coresight.cortex_m import CortexM
from pyocd.core.soc_target import SoCTarget
from pyocd.core.target import Target

from pictorus.command import Command
from pictorus.comms.comms_handler import TelemData
from pictorus.constants import EMPTY_ERROR
from pictorus.postcard.schema.json import JsonSchema
from pictorus.types import LogMessage

try:
    from pyocd.debug.rtt import RTTControlBlock, RTTUpChannel
except ImportError:
    RTTControlBlock = None
from pyocd.core.exceptions import ProbeError, TransferError
import cmsis_pack_manager as cp

from pictorus.date_utils import utc_timestamp_ms
from pictorus.exceptions import CommandError
from pictorus.logging_utils import get_logger, parse_log_entry
from pictorus.config import Config
from .target_manager import TargetManager, TargetMgrConfig

logger = get_logger()
config = Config()

DATA_CHANNEL_ID = 0
LOG_CHANNEL_ID = 1


def _get_matches(cache: cp.Cache, target: str):
    pat = re.compile(fnmatch.translate(target).rsplit("\\Z")[0], re.IGNORECASE)
    return {name for name in cache.index.keys() if pat.search(name)}


def _get_target_name(probe: DebugProbe):
    board_info = probe.associated_board_info
    return board_info.target if board_info else None


def _is_target_installed(target_name: str):
    return (target_name in TARGET) or is_pack_target_available(target_name, Session.get_current())


def _install_target(target_name: str):
    logger.info(f"Installing OCD target: {target_name}")

    cache = cp.Cache(True, False)
    matches = _get_matches(cache, target_name)
    if not matches:
        logger.error(f"Could not find OCD target: {target_name}")
        return

    devices = [cache.index[dev] for dev in matches]
    packs = cache.packs_for_devices(devices)
    logger.info("Downloading packs:")
    for pack in packs:
        logger.info("    " + str(pack))

    cache.download_pack_list(packs)


def _determine_target_name():
    probe = ConnectHelper.choose_probe(
        blocking=False,
        return_first=True,
    )
    if not probe:
        return None

    return _get_target_name(probe)


class ProbeSession:
    # Wrapper around pyocd Session that adds thread synchronization
    def __init__(self, session: Session) -> None:
        self._session = session
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        if not self._session.is_open:
            self._session.open()

        return self._session

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()

    def close(self):
        self._session.close()


class EmbeddedTargetManager(TargetManager):
    def __init__(self, config: TargetMgrConfig) -> None:
        super().__init__(config)
        self._session: Optional[ProbeSession] = None

        self._rtt_complete = threading.Event()
        self._listener_thread: Union[threading.Thread, None] = None
        self.data_chan: Union["RTTUpChannel", None] = None
        self.log_chan: Union["RTTUpChannel", None] = None

    def handle_command(self, cmd: Command):
        try:
            return super().handle_command(cmd)
        except ProbeError as e:
            logger.error("Encountered probe error, disconnecting")
            # If there's an issue with the probe, close the session so we
            # attempt to reconnect on the next command
            self._close_probe()
            raise e

    def _get_session(self):
        if not self._session:
            # This can return None if no targets are found. Need to check this
            # before attempting to use as a ContextManager
            target_name = self._config.target.options.get("ocd_target", _determine_target_name())
            if not target_name:
                logger.error("Unable to determine target type")
                msg = "Unable to choose target type. Verify target is connected and powered on."
                raise CommandError("TargetSelectError", msg)

            target_available = _is_target_installed(target_name)
            if not target_available:
                # Make sure the target index is installed
                futures.wait([self._config.updates_mgr.ocd_update_future])
                _install_target(target_name)

            session = ConnectHelper.session_with_chosen_probe(
                blocking=False,
                return_first=True,
                target_override=target_name,
                connect_mode="attach",
            )
            if not session:
                return None

            self._session = ProbeSession(session)

        return self._session

    def _deploy_app(self):
        self._config.target_state.error_log = EMPTY_ERROR.copy()

        probe = self._get_session()

        flash_success = False

        # Attempt to connect to the target to flash the app. A reconnection may be needed
        # if the user unplugs the USB cable and plugs it back in, interrupting the session.
        for _ in range(2):
            try:
                if not probe:
                    logger.error("Failed to connect to target")
                    raise CommandError(
                        "TargetConnectionError",
                        "Failed to connect to target. Make sure it is connected and powered on.",
                    )

                self._stop_rtt_listener()
                # Connect to the target
                with probe as session:
                    # Create a file programmer and flash the ELF file
                    FileProgrammer(session, no_reset=True).program(
                        self._bin_path, file_format="elf"
                    )
                logger.info("Successfully deployed app to target")
                flash_success = True
                break
            except ProbeError:
                # If there is an issue flashing the device using FileProgrammer, a
                # ProbeError will be raised.
                logger.info("Failed to deploy app, closing probe session")
                self._close_probe()
                probe = self._get_session()

        if not flash_success:
            raise ProbeError(
                "Failed to deploy app after two attempts. "
                "Make sure the target is connected and powered on"
                " and/or try restarting the device manager."
            )

        if self._config.target_state.run_app:
            self._start_app_with_rtt()

    def handle_set_log_level_cmd(self, cmd: Command):
        pass

    def _control_app_running(self, run_app: bool):
        if run_app:
            self._start_app_with_rtt()
        else:
            self._stop_app_and_rtt()

    def close(self):
        self._close_probe()

    def _get_reset_type(self, session: Session) -> Optional[Target.ResetType]:
        if not session.target:
            return None

        return cast("CortexM", session.target.selected_core).default_reset_type

    def _get_target_state(self, session: Session) -> Optional[Target.State]:
        if not session.target:
            return None

        if session.target.selected_core is None:
            # Assume core 0
            session.target.selected_core = 0

        return session.target.get_state()

    def _setup_rtt(self, target: SoCTarget):
        """
        Attempts to set up the RTT channel for sending data. Some chips, like the Cortex-M0+,
        do not support RTT but the code will still run.
        """
        if RTTControlBlock is None:
            return

        try:
            if target.part_number.startswith("STM32H743"):
                # This is a workaround for the STM32H743 where the RTT control block is
                # not found in the usual location. This is a temporary solution until
                # the issue is fixed in pyocd.
                control_block = RTTControlBlock.from_target(
                    target, address=0x24000000, size=0x7D000
                )
            else:
                control_block = RTTControlBlock.from_target(target)

            control_block.start()

            if len(control_block.up_channels) > 0:
                self.data_chan = control_block.up_channels[DATA_CHANNEL_ID]
                data_chan_name = self.data_chan.name if self.data_chan.name is not None else ""
                logger.info(
                    f'Reading logs from RTT up channel {DATA_CHANNEL_ID} \
                            ("{data_chan_name}")'
                )
                if self.data_chan is None:
                    logger.error("Pictorus Device Manager expects an RTT up channel for data.")

                self.log_chan = control_block.up_channels[LOG_CHANNEL_ID]
                log_chan_name = self.log_chan.name if self.log_chan.name is not None else ""
                logger.info(
                    f'Reading logs from RTT up channel {LOG_CHANNEL_ID} \
                            ("{log_chan_name}")'
                )
                if self.log_chan is None:
                    logger.error("Pictorus Device Manager expects an RTT up channel for logs.")

                if self.data_chan is None or self.log_chan is None:
                    logger.error(
                        "Pictorus Device Manager expects two RTT up channels,"
                        " one for data and one for logs."
                    )
                    return

            else:
                logger.info("No RTT channels found, not attempting to read logs")
        except Exception:
            logger.error(
                "Failed to setup RTT for device {}".format(target.part_number),
                exc_info=True,
            )
            logger.info("Running target {} without RTT".format(target.part_number))

    def _start_app_with_rtt(self):
        logger.info("Starting app")
        probe = self._get_session()
        if not probe:
            logger.error("Failed to connect to target")
            return

        self._stop_rtt_listener()
        with probe as session:
            if not session.board:
                logger.error("No board found")
                return

            target: SoCTarget = session.board.target
            self._setup_rtt(target)

            if self._get_target_state(session) == target.State.RUNNING:
                target.resume()
            else:
                target.reset(reset_type=self._get_reset_type(session))

        if self.log_chan is not None and self.data_chan is not None:
            self._start_rtt_listener(self.data_chan, self.log_chan)

    def _stop_app_and_rtt(self):
        logger.info("Stopping app")
        self._stop_rtt_listener()
        probe = self._get_session()
        if not probe:
            logger.error("Failed to connect to target")
            return

        with probe as session:
            if not session.target:
                logger.error("No target found")
                return

            if self._get_target_state(session) != session.target.State.HALTED:
                session.target.reset_and_halt(reset_type=self._get_reset_type(session))

    def _start_rtt_listener(self, data_channel: "RTTUpChannel", log_channel: "RTTUpChannel"):
        # Load the latest telemetry schema
        self._postcard_schema = JsonSchema(self._load_telemetry_schema())

        self._rtt_complete = threading.Event()
        self._listener_thread = threading.Thread(
            target=self._listen_to_rtt, args=(data_channel, log_channel)
        )
        self._listener_thread.start()

    def _stop_rtt_listener(self):
        self._rtt_complete.set()
        if self._listener_thread:
            logger.debug("Stopping listener thread")
            try:
                if self._listener_thread.is_alive():
                    self._listener_thread.join()
            except RuntimeError:
                logger.error("Failed to join listener thread", exc_info=True)
            self._listener_thread = None

    def _close_probe(self):
        self._stop_rtt_listener()

        if self._session:
            with self._session:
                self._session.close()
                self._session = None

    def _listen_to_rtt(self, data_channel: "RTTUpChannel", log_channel: "RTTUpChannel"):
        logger.debug("Listening for logs")

        start_time = datetime.now(timezone.utc)
        last_app_time_us = 0

        postcard_deserializer_error_detected = False

        while not self._rtt_complete.is_set():
            try:
                # poll at most 100 times per second to limit CPU use
                sleep(0.01)

                # read data from up buffer
                probe = self._get_session()
                if not probe:
                    continue

                with probe:
                    data = data_channel.read()  # read data from the data channel
                    log = log_channel.read()  # read data from the log channel

                    if data:
                        # - Deserialize the data bytestream using the postcard format and
                        #   get the list of Dictionary objects that represents one
                        #   measurement point
                        # - Check the app_time_us to ensure there hasn't been a reset
                        # - Add each measurement to the telemetry callback
                        try:
                            json_data = self._deserialize_postcard_bytestream(
                                self._postcard_schema, data
                            )

                            last_telemetry_time = None
                            for telem in json_data:
                                app_time = telem["app_time_us"]
                                if last_app_time_us > app_time:
                                    start_time = datetime.now(timezone.utc)
                                    warning = LogMessage(
                                        timestamp=int(start_time.timestamp() * 1000),
                                        level="warning",
                                        message=(
                                            "App time was reset, this may be due to a "
                                            "reboot of the MCU."
                                        ),
                                    )
                                    self._config.add_log_cb(warning, self._config.target.id)

                                last_app_time_us = app_time
                                last_telemetry_time = start_time + timedelta(microseconds=app_time)

                                self._config.add_telem_cb(
                                    TelemData(
                                        utc_time_ms=utc_timestamp_ms(last_telemetry_time),
                                        build_id=self._config.target_state.build_hash,
                                        data=telem,
                                        target_id=self._config.target.id,
                                    )
                                )

                            # Reset the postcard deserialized error flag if a successful
                            # deserialization occurs
                            postcard_deserializer_error_detected = False
                        except ValueError as exc:
                            if not postcard_deserializer_error_detected:
                                # Only display this message once so we don't overwhelm the log
                                # with the same error
                                logger.error("Failed to deserialize telemetry stream.", exc)
                                self._config.add_log_cb(
                                    LogMessage(
                                        timestamp=int(
                                            datetime.now(timezone.utc).timestamp() * 1000
                                        ),
                                        message=json.dumps(
                                            {
                                                "level": "error",
                                                "message": (
                                                    "Failed to deserialize telemetry stream, "
                                                    "try recompiling and deploying the app."
                                                ),
                                                "device_id": config.client_id,
                                            }
                                        ),
                                    ),
                                    self._config.target.id,
                                )
                                postcard_deserializer_error_detected = True
                            continue

                    if not log:
                        continue

                    # Decode the UTF-8 data from the log channel
                    # and split it into individual log entries
                    # Parse the entry and make sure it is valid, then
                    # add it to the log handler
                    try:
                        entries = log.decode("utf-8").split("\n")
                        entries = [e for e in entries if e]
                        for entry in entries:
                            log_entry = parse_log_entry(
                                entry, datetime.now(timezone.utc), config.client_id, True
                            )
                            if log_entry:
                                logger.info(log_entry)
                                logger.info(self._config.target.id)
                                self._config.add_log_cb(log_entry, self._config.target.id)
                                pass
                    except UnicodeDecodeError:
                        # Sometimes the RTT channels contains default values (0xff) after
                        # a re-flash, we have a ValueError exception for postcard decoding,
                        # so should have one for log decoding as well.
                        continue

            except (ProbeError, TransferError):
                # This can happen if a user unplugs the USB cable, try to handle
                # this gracefully by closing the session.
                logger.error("Error with with connection to probe", exc_info=True)
                self._close_probe()
                break
