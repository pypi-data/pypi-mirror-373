from dataclasses import asdict
import json
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from awscrt import mqtt
from awsiot.iotshadow import ShadowDeltaUpdatedEvent
from cbor2 import dumps as cbor_dumps

from pictorus.command import CmdType, Command, CommandResult, StatusCode
from pictorus.comms.comms_handler import CommsConfig, TelemData
from pictorus.comms.mqtt_comms_handler import MqttCommsHandler
from pictorus.config import Config
from pictorus.types import DeviceState, LogMessage, TargetState
from tests.utils import wait_for_condition

global_config = Config()


class TestMqttCommsHandler(TestCase):
    def setUp(self) -> None:
        self.m_process_cmd = Mock()
        self.m_sync_device_state = Mock()
        config = CommsConfig(
            process_cmd=self.m_process_cmd,
            sync_device_state=self.m_sync_device_state,
        )
        self.m_mqtt_connection = MagicMock(spec=mqtt.Connection)
        with patch(
            "pictorus.comms.mqtt_comms_handler.mqtt_connection_builder.mtls_from_bytes",
            return_value=self.m_mqtt_connection,
        ):
            self.handler = MqttCommsHandler(config)

        self.addCleanup(self.handler.close)

    def test_starts_and_stops_app_based_on_shadow(self):
        target_id = "foo"
        # Start the app
        self.handler._on_shadow_delta_updated(
            ShadowDeltaUpdatedEvent(state={"target_states": {target_id: {"run_app": True}}})
        )
        self.m_process_cmd.assert_called_once_with(
            Command(
                type=CmdType.RUN_APP,
                data={"run_app": True},
                target_id=target_id,
            ),
            None,
        )
        self.m_mqtt_connection.publish.assert_not_called()

        # Stop the app
        self.m_process_cmd.reset_mock()
        self.handler._on_shadow_delta_updated(
            ShadowDeltaUpdatedEvent(state={"target_states": {target_id: {"run_app": False}}})
        )
        self.m_process_cmd.assert_called_once_with(
            Command(
                type=CmdType.RUN_APP,
                data={"run_app": False},
                target_id=target_id,
            ),
            None,
        )
        self.m_mqtt_connection.publish.assert_not_called()

    def test_resubscribes_to_topics_and_republishes_shadow_state_on_reconnect(self):
        m_connection = Mock()
        self.handler._on_connection_resumed(m_connection, mqtt.ConnectReturnCode.ACCEPTED, False)
        m_connection.resubscribe_existing_topics.assert_called_once()
        self.m_sync_device_state.assert_called_once()

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
        self.handler._on_cmd_request(command.to_dict(), "foo")
        self.m_mqtt_connection.publish.reset_mock()

        data = {"foo": 1.0}
        self.handler.add_telemetry(
            TelemData(
                utc_time_ms=utc_time_ms,
                build_id=build_hash,
                data=data,
                target_id=target_id,
            )
        )

        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)
        expected_payload = {"foo": [1.0], "utctime": [utc_time_ms]}
        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"dt/pictorus/{global_config.client_id}/stream/{target_id}/telem",
            payload=cbor_dumps(expected_payload),
            qos=mqtt.QoS.AT_MOST_ONCE,
        )

    @patch.object(MqttCommsHandler, "LOG_BATCH_SIZE", 1)
    def test_add_log(self):
        target_id = "test_target"

        # Set TTL to make sure data is published
        command = Command(
            type=CmdType.SET_TELEMETRY_TLL,
            data={"ttl_s": 60},
            target_id=target_id,
        )
        self.handler._on_cmd_request(command.to_dict(), "foo")
        self.m_mqtt_connection.publish.reset_mock()

        msg = LogMessage(
            timestamp=1672531200000,
            level="info",
            message="foo",
        )
        self.handler.add_log(msg, target_id)

        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)

        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"dt/pictorus/{global_config.client_id}/stream/{target_id}/logs",
            payload=json.dumps([asdict(msg)]),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def test_update_device_state(self):
        reported_state = DeviceState(
            connected=True, version="1.0.0", target_states={"foo": TargetState(run_app=True)}
        )
        desired_state = DeviceState(target_states={"foo": TargetState(run_app=False)})

        self.handler.update_device_state(reported_state, desired_state)

        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)

        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"$aws/things/{global_config.client_id}/shadow/update",
            payload=json.dumps(
                {
                    "state": {
                        "desired": {"target_states": {"foo": {"run_app": False}}},
                        "reported": asdict(reported_state),
                    }
                }
            ),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

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

        self.handler._on_cmd_request(command.to_dict(), "foo")

        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)

        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"cmd/pictorus/{global_config.client_id}/res",
            payload=json.dumps(result.to_dict()),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def test_handles_invalid_command_and_publishes_error(self):
        cmd_id = "cmd1"
        cmd_data = {"id": cmd_id, "foo": "bar"}  # Invalid command data

        self.m_process_cmd.side_effect = ValueError("Invalid command")

        self.handler._on_cmd_request(cmd_data, "foo")

        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)
        expected_result = CommandResult(id=cmd_id, type=CmdType.UNKNOWN, status=StatusCode.ERROR)
        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"cmd/pictorus/{global_config.client_id}/res",
            payload=json.dumps(expected_result.to_dict()),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def test_handle_command_skips_publish_if_no_id(self):
        target_id = "test_target"
        command = Command(
            type=CmdType.UPDATE_APP,
            data={"app_version": "1.0.0"},
            target_id=target_id,
        )

        self.m_process_cmd.return_value = None

        self.handler._on_cmd_request(command.to_dict(), "foo")

        wait_for_condition(lambda: self.m_process_cmd.call_count > 0)
        self.m_mqtt_connection.publish.assert_not_called()

    def test_handles_set_ttl_command(self):
        target_id = "test_target"
        command = Command(
            type=CmdType.SET_TELEMETRY_TLL,
            data={"ttl_s": 120},
            target_id=target_id,
        )

        assert not self.handler._is_ttl_active(target_id)
        self.handler._on_cmd_request(command.to_dict(), "foo")
        wait_for_condition(lambda: self.m_mqtt_connection.publish.call_count > 0)
        assert self.handler._is_ttl_active(target_id)

        expected = CommandResult(
            id=command.id,
            type=CmdType.SET_TELEMETRY_TLL,
            status=StatusCode.SUCCESS,
        )
        self.m_mqtt_connection.publish.assert_called_once_with(
            topic=f"cmd/pictorus/{global_config.client_id}/res",
            payload=json.dumps(expected.to_dict()),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
