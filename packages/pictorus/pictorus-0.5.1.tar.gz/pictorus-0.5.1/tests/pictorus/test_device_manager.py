from dataclasses import asdict
import json
from typing import Union
from unittest import TestCase
from unittest.mock import ANY, MagicMock, mock_open, patch, Mock
import time

from aiortc import RTCSessionDescription
import responses

from pictorus.command import CmdType, Command, DeployTarget
from pictorus.comms.comms_handler import CommsConfig
from pictorus.comms.webrtc_comms_handler import RTCOfferData
from pictorus.config import Config
from pictorus.constants import PICTORUS_SERVICE_NAME
from pictorus.device_manager import DeviceManager
from pictorus.logging_utils import get_logger
from pictorus.types import DeviceState, TargetState

config = Config()
logger = get_logger()

ADDR_DATA = ("127.0.0.1", 1234)
BUILD_HASH = "bob"


@patch(
    "pictorus.device_manager.load_app_manifest",
    new=Mock(return_value={"build_hash": BUILD_HASH, "params_hash": "bar"}),
)
class TestDeviceManager(TestCase):
    def setUp(self):
        self.start_time = time.time()
        config.store_config(
            {
                "clientId": "foo_device",
                "mqttEndpoint": "foo_endpoint",
                "credentials": {
                    "certificatePem": "foo_cert",
                    "certificateCa": "foo_ca",
                    "keyPair": {
                        "PrivateKey": "foo_key",
                    },
                },
            }
        )

        self.captured_config: Union[CommsConfig, None] = None
        self.m_mqtt_handler = Mock()

        # Capture the config so we can call the command callback
        def m_mqtt_constructor(config: CommsConfig):
            self.captured_config = config
            return self.m_mqtt_handler

        mqtt_patch = patch(
            "pictorus.device_manager.MqttCommsHandler", side_effect=m_mqtt_constructor
        )
        mqtt_patch.start()
        self.addCleanup(mqtt_patch.stop)

        webrtc_patch = patch("pictorus.device_manager.WebRtcCommsHandler")
        m_webrtc = webrtc_patch.start()
        self.m_webrtc_handler = m_webrtc.return_value
        self.addCleanup(webrtc_patch.stop)

    def test_run_deleted_target_removes_from_desired_state(self):
        target_id = "foo"

        run_app_cmd = Command(
            id="1",
            type=CmdType.RUN_APP,
            data={"run_app": True},
            target_id=target_id,
        )
        expected_desired_state = DeviceState(
            target_states={target_id: None}  # Target is deleted, so no state
        )

        with DeviceManager(Mock()):
            assert self.captured_config
            # Attempt to start an app for a target that doesn't exist
            self.captured_config.process_cmd(run_app_cmd, None)
            self.m_mqtt_handler.update_device_state.assert_any_call(
                reported_state=ANY,
                desired_state=expected_desired_state,
            )
            self.m_webrtc_handler.update_device_state.assert_any_call(
                reported_state=ANY,
                desired_state=expected_desired_state,
            )

    @responses.activate
    @patch("pictorus.device_manager.get_daemon")
    def test_set_upload_logs(self, m_get_daemon):
        upload_url = "https://example.com/upload"

        upload_logs_cmd = Command(
            id="1",
            type=CmdType.UPLOAD_LOGS,
            data={
                "upload_dest": {"url": upload_url, "fields": {"foo": "bar"}},
                "line_count": 500,
            },
            # Kind of dumb, but we require a target ID to be set.
            # Maybe should be optional for commands that aren't target specific
            target_id="",
        )
        responses.add(responses.POST, upload_url, body="")
        with DeviceManager(Mock()):
            assert self.captured_config
            self.captured_config.process_cmd(upload_logs_cmd, None)
            m_get_daemon.return_value.logs.assert_called_once_with(
                service_name=PICTORUS_SERVICE_NAME, number_of_lines=500
            )

    def test_handles_run_app_command(self):
        target_id = "foo"
        target = DeployTarget({"id": target_id, "type": "process"})
        target_state = TargetState(build_hash=BUILD_HASH)
        manifest_data = {
            "targets": [target.to_dict()],
            "target_states": {target_id: asdict(target_state)},
        }

        target_mgr = MagicMock()
        target_mgr.target = target
        target_mgr.target_state = target_state

        m_write = mock_open()
        with DeviceManager(Mock()) as mgr, patch("builtins.open", m_write):
            assert self.captured_config

            mgr._target_managers = {target_id: target_mgr}
            # Start the app
            cmd = Command(
                id="1",
                type=CmdType.RUN_APP,
                data={"run_app": True},
                target_id=target_id,
            )
            self.captured_config.process_cmd(cmd, None)
            target_mgr.handle_command.assert_called_once_with(cmd)
            handle = m_write()
            handle.write.assert_called_once_with(json.dumps(manifest_data))
            assert self.m_mqtt_handler.update_device_state.mock_calls[1][2][
                "reported_state"
            ].target_states == {target_id: target_state}

            # Stop the app
            target_mgr.handle_command.reset_mock()
            cmd = Command(
                id="1",
                type=CmdType.RUN_APP,
                data={"run_app": False},
                target_id=target_id,
            )
            self.captured_config.process_cmd(cmd, None)
            target_mgr.handle_command.assert_called_once_with(cmd)

    def test_handles_webrtc_offer_command(self):
        target_id = "foo"
        with DeviceManager(Mock()):
            assert self.captured_config

            offer_data = {
                "offer": {
                    "type": "offer",
                    "sdp": "fake_offer",
                },
                "session_id": "session-123",
            }
            # Handle WebRTC offer command
            cmd = Command(
                id="1",
                type=CmdType.WEBRTC_OFFER,
                data=offer_data,
                target_id=target_id,
            )
            self.captured_config.process_cmd(cmd, None)
            expected = RTCOfferData(
                session_id=offer_data["session_id"],
                offer=RTCSessionDescription(
                    sdp=offer_data["offer"]["sdp"], type=offer_data["offer"]["type"]
                ),
            )
            self.m_webrtc_handler.accept_offer.assert_called_once_with(expected)
