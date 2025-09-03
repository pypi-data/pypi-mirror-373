from abc import ABC, abstractmethod
import json
import os
from typing import Any, Callable, Dict, List
from dataclasses import dataclass

import cobs.cobs
import requests

from pictorus.comms.comms_handler import TelemData
from pictorus.exceptions import CommandError
from pictorus.postcard.schema.core import Schema
from pictorus.postcard.schema.json import JsonSchema
from pictorus.types import ErrorLog, LogMessage, TargetState
from pictorus.updates_manager import UpdatesManager
from pictorus.config import APP_ASSETS_DIR
from pictorus.command import Command, DeployTarget, DeployTargetType, CmdType
from pictorus.logging_utils import get_logger


logger = get_logger()


def _is_process_target(target: DeployTarget) -> bool:
    return target.type == DeployTargetType.PROCESS


def _download_file(file_path: str, url: str):
    """Download a file to specified path"""
    logger.info("Downloading url: %s to path: %s", url, file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with requests.get(url, stream=True) as req, open(file_path, "wb") as in_file:
        req.raise_for_status()
        for chunk in req.iter_content(chunk_size=8192):
            in_file.write(chunk)


@dataclass
class TargetMgrConfig:
    target: DeployTarget
    target_state: TargetState
    updates_mgr: UpdatesManager
    sync_device_state_cb: Callable[[], None]
    add_log_cb: Callable[[LogMessage, str], None]
    add_telem_cb: Callable[[TelemData], None]


class TargetManager(ABC):
    def __init__(
        self,
        config: TargetMgrConfig,
    ) -> None:
        target = config.target
        logger.info("Initializing %s target with ID: %s", target.type.value, target.id)
        self._config = config
        self._assets_dir = os.path.join(APP_ASSETS_DIR, target.id)
        self._bin_path = os.path.join(self._assets_dir, "pictorus_managed_app")
        self._params_path = os.path.join(self._assets_dir, "diagram_params.json")
        self._postcard_schema = JsonSchema({})

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def target_state(self) -> TargetState:
        """Get the target state object"""
        return self._config.target_state

    @property
    def target_id(self) -> str:
        return self._config.target.id

    @property
    def target(self) -> DeployTarget:
        """Get the target object"""
        return self._config.target

    def handle_command(self, cmd: Command):
        """Handle a command"""
        try:
            if cmd.type == CmdType.UPDATE_APP:
                self.handle_update_app_cmd(cmd)
            elif cmd.type == CmdType.SET_LOG_LEVEL:
                self.handle_set_log_level_cmd(cmd)
            elif cmd.type == CmdType.RUN_APP:
                self.handle_run_app_cmd(cmd)
            else:
                logger.warning("Unknown command: %s", cmd.type)
        except CommandError as e:
            logger.error("Failed to handle command: %s", e)
            self._config.target_state.error_log = ErrorLog(err_type=e.err_type, message=e.message)
            raise e
        except Exception as e:
            logger.error("Failed to handle command: %s", e, exc_info=True)
            self._config.target_state.error_log = ErrorLog(
                err_type="UnknownError", message=f"Command failed: {e}"
            )
            raise e

    def handle_update_app_cmd(self, cmd: Command):
        """Update the app version for this target"""
        self._download_app_files(cmd)
        self._deploy_app()

    @abstractmethod
    def handle_set_log_level_cmd(self, cmd: Command):
        """Set the log level for this target"""
        pass

    def handle_run_app_cmd(self, cmd: Command):
        """Control whether the app is running or not"""
        run_app = cmd.data["run_app"]
        self._config.target_state.run_app = run_app
        self._control_app_running(run_app)

    @abstractmethod
    def _deploy_app(self):
        """Deploy the app to the target"""
        pass

    @abstractmethod
    def _control_app_running(self, run_app: bool):
        """
        Start/stop the app.

        This is used by some internal methods so is separated from
        the public method for handling commands
        """
        pass

    def open(self):
        """Open the target manager"""
        # Note: Since there may be multiple embedded targets per device manager,
        # these targets need to be managed a little more carefully. Opening the
        # embedded target (calling _control_app_running) is done when
        # handling commands in the handle_command method.
        pass

    @abstractmethod
    def close(self):
        """Close the target manager"""
        pass

    def _load_telemetry_schema(self) -> Dict[str, str]:
        schema = {}
        # Load the latest telemetry parameters file
        if not os.path.exists(self._params_path):
            logger.error(
                (
                    "Postcard parameters file not found, try re-compiling and deploying the app."
                    "Telemetry will not be available until this is fixed."
                )
            )
        else:
            with open(self._params_path, "r") as f:
                schema = json.load(f)
                schema = schema.get("telemetry_schema")
                if schema is None:
                    logger.error(
                        "Telemetry schema not found in parameters file, for target %s, "
                        "try re-compiling and deploying the app.",
                        self._config.target.id,
                    )
                    raise CommandError(
                        "TelemetrySchemaNotFound",
                        (
                            "Telemetry schema not found in parameters file. Try re-compiling"
                            " and deploying the app."
                        ),
                    )

                logger.info(
                    "Loaded telemetry schema for target %s: %s", self._config.target.id, schema
                )

        return schema

    def _deserialize_postcard_bytestream(self, schema: Schema, data: bytes) -> List[Dict[str, Any]]:
        """
        Deserialize a COBS-encoded Postcard bytestream using a given schema.
        """
        packets = bytes.split(data, b"\x00")

        as_json = []  # A List of JSON objects, each entry represents a measurement

        for packet in packets:
            if packet:
                uncobs = cobs.cobs.decode(packet)
                deserialized = schema.convert(bytearray(uncobs))
                as_json.append(deserialized)

        return as_json

    def _download_app_files(self, cmd: Command):
        build_hash = cmd.data.get("build_hash")
        app_bin_url = cmd.data.get("app_bin_url")
        params_hash = cmd.data.get("params_hash")
        params_url = cmd.data.get("params_url")

        params_valid = (
            params_hash and params_url if _is_process_target(self._config.target) else True
        )
        if not build_hash or not app_bin_url or not params_valid:
            logger.error("Invalid app update request: %s", cmd.data)
            raise CommandError("InvalidUpdateRequest", "Missing required fields for app update.")

        download_paths = []
        if self._config.target_state.build_hash != build_hash:
            logger.info("Updating binary")
            download_paths.append((self._bin_path, app_bin_url))

        if self._config.target_state.params_hash != params_hash and params_url:
            logger.info("Updating params")
            download_paths.append((self._params_path, params_url))

        if download_paths:
            # For a process target we need to stop the app to make sure it's not busy.
            # Otherwise the OS will refuse to overwrite it
            if _is_process_target(self._config.target):
                self._control_app_running(False)

            try:
                for path, url in download_paths:
                    _download_file(path, url)
            except requests.exceptions.HTTPError:
                logger.error("Failed to update app", exc_info=True)
                raise CommandError("DownloadError", "Failed to download app files.")
            else:
                os.chmod(self._bin_path, 0o755)
                self._config.target_state.build_hash = build_hash
                self._config.target_state.params_hash = params_hash
                logger.info("Successfully updated app")
        else:
            logger.info("Using cached app files")
