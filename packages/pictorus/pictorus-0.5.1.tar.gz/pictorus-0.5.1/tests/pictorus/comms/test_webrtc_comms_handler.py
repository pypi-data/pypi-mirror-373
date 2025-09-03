from dataclasses import asdict
import json
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from aiortc import RTCDataChannel, RTCPeerConnection, RTCSessionDescription
from cbor2 import dumps as cbor_dumps

from pictorus.command import CmdType, Command, CommandResult, StatusCode
from pictorus.comms.comms_handler import CommsConfig, TelemData
from pictorus.comms.webrtc_comms_handler import ChannelType, RTCOfferData, WebRtcCommsHandler
from pictorus.config import Config
from pictorus.types import LogMessage
from tests.utils import wait_for_condition

global_config = Config()


class TestWebRtcCommsHandler(TestCase):
    SESSION_ID = "test_session_id"

    def setUp(self) -> None:
        self.m_process_cmd = Mock()
        self.m_sync_device_state = Mock()
        config = CommsConfig(
            process_cmd=self.m_process_cmd,
            sync_device_state=self.m_sync_device_state,
        )
        self.handler = WebRtcCommsHandler(config)
        offer = RTCOfferData(
            session_id=self.SESSION_ID, offer=RTCSessionDescription(sdp="offer-sdp", type="offer")
        )

        # Set up the peer connection and data channels
        self.m_peer_connection = MagicMock(spec=RTCPeerConnection)
        self.m_peer_connection.localDescription.sdp = "answer-sdp"
        self.m_peer_connection.localDescription.type = "answer"

        self.m_telem_channel = MagicMock(spec=RTCDataChannel, label=ChannelType.TELEMETRY.value)
        self.m_log_channel = MagicMock(spec=RTCDataChannel, label=ChannelType.LOGS.value)
        self.m_cmd_channel = MagicMock(spec=RTCDataChannel, label=ChannelType.COMMANDS.value)
        with patch(
            "pictorus.comms.webrtc_comms_handler.RTCPeerConnection",
            return_value=self.m_peer_connection,
        ):
            self.handler.accept_offer(offer)

        self.addCleanup(self.handler.close)
        self.handler._handle_data_channel_created(self.SESSION_ID, self.m_cmd_channel)
        self.handler._handle_data_channel_created(self.SESSION_ID, self.m_log_channel)
        self.handler._handle_data_channel_created(self.SESSION_ID, self.m_telem_channel)

    def test_add_telemetry(self):
        target_id = "test_target"
        build_hash = "test_build_hash"
        utc_time_ms = 1672531200000

        # Set TTL to make sure data is published
        command = Command(
            type=CmdType.SET_TELEMETRY_TLL,
            data={"ttl_s": 60},
            target_id=target_id,
        )
        self.handler._on_cmd_request(command.to_dict(), self.SESSION_ID)

        data = {"foo": 1.0}
        self.handler.add_telemetry(
            TelemData(
                utc_time_ms=utc_time_ms,
                build_id=build_hash,
                data=data,
                target_id=target_id,
            )
        )

        wait_for_condition(lambda: self.m_telem_channel.send.call_count > 0)
        expected_payload = {"foo": [1.0], "utctime": [utc_time_ms]}
        self.m_telem_channel.send.assert_called_once_with(cbor_dumps(expected_payload))

    @patch.object(WebRtcCommsHandler, "LOG_BATCH_SIZE", 1)
    def test_add_log(self):
        target_id = "test_target"
        # Set TTL to make sure data is published
        command = Command(
            type=CmdType.SET_TELEMETRY_TLL,
            data={"ttl_s": 60},
            target_id=target_id,
        )
        self.handler._on_cmd_request(command.to_dict(), self.SESSION_ID)

        msg = LogMessage(
            timestamp=1672531200000,
            level="info",
            message="foo",
        )
        self.handler.add_log(msg, target_id)

        wait_for_condition(lambda: self.m_log_channel.send.call_count > 0)
        self.m_log_channel.send.assert_called_once_with(json.dumps([asdict(msg)]))

    def test_handles_command_and_publishes_the_result(self):
        target_id = "test_target"
        cmd_id = "cmd1"
        command = Command(
            id=cmd_id,
            type=CmdType.UPDATE_APP,
            data={"app_version": "1.0.0"},
            target_id=target_id,
        )

        result = CommandResult(id=cmd_id, type=CmdType.UPDATE_APP, status=StatusCode.SUCCESS)
        self.m_process_cmd.return_value = result
        self.handler._on_cmd_request(command.to_dict(), self.SESSION_ID)

        wait_for_condition(lambda: self.m_cmd_channel.send.call_count > 0)
        self.m_cmd_channel.send.assert_called_once_with(json.dumps(result.to_dict()))

    def test_handles_invalid_command_and_publishes_error(self):
        cmd_id = "cmd1"
        cmd_data = {"id": cmd_id, "foo": "bar"}  # Invalid command data

        self.m_process_cmd.side_effect = ValueError("Invalid command")

        self.handler._on_cmd_request(cmd_data, self.SESSION_ID)
        wait_for_condition(lambda: self.m_cmd_channel.send.call_count > 0)
        expected_result = CommandResult(
            id=cmd_id,
            type=CmdType.UNKNOWN,
            status=StatusCode.ERROR,
        )
        self.m_cmd_channel.send.assert_called_once_with(json.dumps(expected_result.to_dict()))

    def test_handle_command_skips_publish_if_no_id(self):
        target_id = "test_target"
        command = Command(
            type=CmdType.UPDATE_APP,
            data={"app_version": "1.0.0"},
            target_id=target_id,
        )

        self.m_process_cmd.return_value = None

        self.handler._on_cmd_request(command.to_dict(), self.SESSION_ID)
        wait_for_condition(lambda: self.m_process_cmd.call_count > 0)
        self.m_cmd_channel.send.assert_not_called()

    def test_handles_set_ttl_command(self):
        target_id = "test_target"
        command = Command(
            type=CmdType.SET_TELEMETRY_TLL,
            data={"ttl_s": 120},
            target_id=target_id,
        )

        assert not self.handler._is_ttl_active(target_id)
        self.handler._on_cmd_request(command.to_dict(), self.SESSION_ID)
        wait_for_condition(lambda: self.m_cmd_channel.send.call_count > 0)
        assert self.handler._is_ttl_active(target_id)

        expected = CommandResult(
            id=command.id,
            type=CmdType.SET_TELEMETRY_TLL,
            status=StatusCode.SUCCESS,
        )
        self.m_cmd_channel.send.assert_called_once_with(json.dumps(expected.to_dict()))
