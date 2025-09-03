import os
import threading
from typing import Dict, List, Union
import json
import time
from dataclasses import asdict

from awscrt import mqtt
from awsiot import iotshadow, mqtt_connection_builder
from awscrt.exceptions import AwsCrtError
from cbor2 import dumps as cbor_dumps

from pictorus.command import CmdType, Command, CommandResult, StatusCode
from pictorus.comms.comms_handler import TelemData
from pictorus.comms.streaming_comms_handler import StreamingCommsConfig, StreamingCommsHandler
from pictorus.config import Config
from pictorus.constants import THREAD_SLEEP_TIME_S
from pictorus.logging_utils import get_logger
from pictorus.types import DeviceState, LogMessage
from .comms_handler import CommsConfig

CONNECT_RETRY_TIMEOUT_S = 15

global_config = Config()
logger = get_logger()


def _cmd_topic(subtopic: str):
    return f"cmd/pictorus/{global_config.client_id}/{subtopic}"


def _stream_topic(target_id: str, stream: str):
    """Get the topic for a specific stream for a target"""
    return f"dt/pictorus/{global_config.client_id}/stream/{target_id}/{stream}"


def _get_basic_ingest_topic(rule_name: str, topic: str):
    """Get the basic ingest topic for a given rule and base topic"""
    return os.path.join("$aws/rules/", rule_name, topic)


def _connect_mqtt(mqtt_connection: mqtt.Connection):
    connect_future = mqtt_connection.connect()
    while True:
        try:
            connect_future.result()
            break
        except AwsCrtError:
            logger.warning(
                "Connection failed. Retrying in: %ss", CONNECT_RETRY_TIMEOUT_S, exc_info=True
            )
            connect_future = mqtt_connection.connect()
            time.sleep(CONNECT_RETRY_TIMEOUT_S)

    logger.info("Connected to MQTT broker")


class MqttCommsHandler(StreamingCommsHandler):
    """MQTT communication handler for Pictorus."""

    CMD_REQUEST_SUBTOPIC = "req"
    RETAINED_CMD_SUBTOPIC = "ret"

    # Config for publishing log streams
    LOG_PUBLISH_INTERVAL = 1  # 1 Hz
    LOG_BATCH_SIZE = 100
    LOG_MAX_QUEUE_SIZE = 1000

    # Config for publishing telemetry streams
    TELEM_PUBLISH_INTERVAL_S = 0.1  # 10 Hz
    TELEM_BATCH_SIZE = 1000
    TELEM_MAX_QUEUE_SIZE = 10000

    # Config for publishing telem for persistence
    # TODO: This is just a bandaid to allow us to support loading telemetry
    # via public APIs. Eventually this should be unified with the telemetry stream
    # or some other more robust persistence mechanism.
    TELEM_PERSISTENCE_INTERVAL_MS = 50

    def __init__(self, config: CommsConfig):
        streaming_config = StreamingCommsConfig(
            sync_device_state=config.sync_device_state,
            process_cmd=config.process_cmd,
            telem_publish_interval_s=self.TELEM_PUBLISH_INTERVAL_S,
            telem_batch_size=self.TELEM_BATCH_SIZE,
            telem_max_queue_size=self.TELEM_MAX_QUEUE_SIZE,
            log_publish_interval_s=self.LOG_PUBLISH_INTERVAL,
            log_batch_size=self.LOG_BATCH_SIZE,
            log_max_queue_size=self.LOG_MAX_QUEUE_SIZE,
        )
        super().__init__(streaming_config)
        self._complete = threading.Event()

        self._mqtt_connection = self._create_mqtt_connection()
        # Thread to establish the MQTT connection. This is marked as a daemon so we can
        # still exit the program if we fail to ever establish a connection.
        threading.Thread(target=_connect_mqtt, args=(self._mqtt_connection,), daemon=True).start()

        self._mqtt_connection.subscribe(
            _cmd_topic(self.CMD_REQUEST_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_standard_cmd,
        )

        self._mqtt_connection.subscribe(
            _cmd_topic(self.RETAINED_CMD_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_retained_cmd,
        )

        self._last_published_shadow_state = None
        self._shadow_client = iotshadow.IotShadowClient(self._mqtt_connection)
        self._shadow_client.subscribe_to_shadow_delta_updated_events(
            request=iotshadow.ShadowDeltaUpdatedSubscriptionRequest(
                thing_name=global_config.client_id
            ),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_shadow_delta_updated,
        )

        self._legacy_message_topic = _get_basic_ingest_topic(
            "app_telemetry_test",
            f"dt/pictorus/{global_config.client_id}/telem",
        )
        self._last_legacy_persist_ms = 0
        self._legacy_target_ids = set()

        # Thread to manage data publishing. This was originally managed by the base class,
        # but I ran into issues with event loop management in the WebRTC handler.
        self._publish_check_thread = threading.Thread(target=self._poll_publish_data)
        self._publish_check_thread.start()

    def add_log(self, log: LogMessage, target_id: str):
        # Don't publish logs for legacy target IDs since they aren't consumed by anything
        if target_id not in self._legacy_target_ids:
            return super().add_log(log, target_id)

    def add_telemetry(self, data: TelemData) -> None:
        if data.target_id not in self._legacy_target_ids:
            # If the target ID is not in the legacy list, use the streaming handler
            return super().add_telemetry(data)

        ttl_active = self._is_ttl_active(data.target_id)
        if (
            ttl_active
            and data.utc_time_ms - self._last_legacy_persist_ms
            >= self.TELEM_PERSISTENCE_INTERVAL_MS
        ):
            self._publish_legacy_telem(data)

    def update_device_state(
        self, reported_state: DeviceState, desired_state: Union[DeviceState, None] = None
    ):
        """Update the device state in the communication queue."""
        state_data = {"reported": asdict(reported_state)}
        desired_data = desired_state.to_desired_dict() if desired_state else None
        if desired_data:
            state_data["desired"] = desired_data

        logger.info("Updating shadow state: %s", state_data)
        # Don't publish an update if nothing changed. Otherwise we can get in a bad state
        # where IoT backend continuously publishes deltas and we respond with the
        # same reported state
        if state_data == self._last_published_shadow_state:
            return

        request = iotshadow.UpdateShadowRequest(
            thing_name=global_config.client_id,
            state=iotshadow.ShadowState(**state_data),
        )
        self._shadow_client.publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)
        self._last_published_shadow_state = state_data

    def close(self):
        super().close()
        self._mqtt_connection.unsubscribe(_cmd_topic(self.CMD_REQUEST_SUBTOPIC))
        self._mqtt_connection.unsubscribe(_cmd_topic(self.RETAINED_CMD_SUBTOPIC))

        if self._mqtt_connection:
            try:
                self._mqtt_connection.disconnect().result(timeout=10)
            except Exception as e:
                logger.error("Error disconnecting MQTT connection: %s", e, exc_info=True)

        if self._publish_check_thread and self._publish_check_thread.is_alive():
            self._publish_check_thread.join()

        logger.info("MQTT connection closed")

    def _poll_publish_data(self):
        """
        Periodically check if there is data to publish and publish it.
        """
        while not self._complete.is_set():
            self._check_publish_data()
            time.sleep(THREAD_SLEEP_TIME_S)

    def _on_standard_cmd(self, topic: str, payload: bytes):
        return self._on_cmd_request(json.loads(payload))

    def _on_retained_cmd(self, topic: str, payload: bytes):
        # This is an echo of the message we published to clear the retained message
        if not payload:
            return

        try:
            self._on_cmd_request(json.loads(payload))
        finally:
            # This is a retained message so clear it by publishing an empty payload
            # This is a barebones implementation for being able to queue actions for a device.
            # Right now it only allows a single queued command.
            # Eventually we can implement the full jobs API for more robust control of actions
            self._mqtt_connection.publish(
                topic=topic,
                payload="",
                qos=mqtt.QoS.AT_LEAST_ONCE,
                retain=True,
            )

    def _publish_cmd_result(self, result: CommandResult, stream_id: Union[str, None] = None):
        """Publish the result of a command to the MQTT broker."""
        topic = _cmd_topic("res")
        payload = json.dumps(result.to_dict())

        self._mqtt_connection.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def _publish_logs(self, target_id: str, logs: List[LogMessage]):
        self._mqtt_connection.publish(
            topic=_stream_topic(target_id, "logs"),
            payload=json.dumps(list(map(asdict, logs))),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def _publish_telemetry(self, target_id: str, data: Dict[str, List]):
        self._mqtt_connection.publish(
            topic=_stream_topic(target_id, "telem"),
            # We use CBOR since it compresses more efficiently than JSON with large numeric data
            payload=cbor_dumps(data),
            qos=mqtt.QoS.AT_MOST_ONCE,
        )

    def _process_internal_cmd(
        self, cmd: Command, stream_id: Union[str, None] = None
    ) -> CommandResult:
        status = StatusCode.ERROR
        if cmd.type == CmdType.SET_TELEMETRY_TLL:
            ttl_s = cmd.data.get("ttl_s", 0)
            self.set_ttl(ttl_s, cmd.target_id)
            # In order to support legacy workflows where we interact with device manager
            # via public APIs, we need to be able to switch between legacy telem topics
            # and new streaming topics.
            use_legacy_persistence = cmd.data.get("use_legacy_persistence", False)
            if use_legacy_persistence:
                self._legacy_target_ids.add(cmd.target_id)
            else:
                self._legacy_target_ids.discard(cmd.target_id)

            status = StatusCode.SUCCESS

        return CommandResult(
            id=cmd.id,
            status=status,
            type=cmd.type,
        )

    def _create_mqtt_connection(self):
        """Connect to the MQTT broker"""
        # AWS does not update device shadows from LWT messages, so we need to publish
        # to a standard topic and then republish on the backend:
        # https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-comms-app.html#thing-connection
        lwt = mqtt.Will(
            topic=f"my/things/{global_config.client_id}/shadow/update",
            qos=1,
            payload=json.dumps({"state": {"reported": {"connected": False}}}).encode(),
            retain=False,
        )
        mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
            client_id=global_config.client_id,
            endpoint=global_config.mqtt_endpoint,
            cert_bytes=global_config.credentials["certificatePem"].encode(),
            pri_key_bytes=global_config.credentials["keyPair"]["PrivateKey"].encode(),
            ca_bytes=global_config.credentials["certificateCa"].encode(),
            on_connection_interrupted=self._on_connection_interrupted,
            on_connection_resumed=self._on_connection_resumed,
            will=lwt,
            keep_alive_secs=30,
            reconnect_min_timeout_secs=5,
            reconnect_max_timeout_secs=30,
        )

        return mqtt_connection

    def _on_shadow_delta_updated(self, delta: iotshadow.ShadowDeltaUpdatedEvent):
        if not delta.state:
            return

        state = DeviceState.from_dict(delta.state)
        logger.debug("Received shadow delta: %s", state)

        if state.target_states:
            run_app_changes = {
                target_id: target_state.run_app
                for target_id, target_state in state.target_states.items()
                if target_state
            }
            for target_id, run_app in run_app_changes.items():
                run_cmd = Command(
                    type=CmdType.RUN_APP,
                    data={"run_app": run_app},
                    # Normally commands pass in a full target object,
                    # but we don't have a way to do that currently with shadow deltas
                    target_id=target_id,
                )
                self._config.process_cmd(run_cmd, None)

    def _on_connection_interrupted(self, connection, error, **kwargs):
        # Callback when connection is accidentally lost.
        logger.warning("Connection interrupted. error: %s", error)

    def _on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        # Callback when an interrupted connection is re-established.
        logger.info(
            "Connection resumed. return_code: %s session_present: %s", return_code, session_present
        )

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            logger.debug("Session did not persist. Resubscribing to existing topics...")
            connection.resubscribe_existing_topics()

        # Re-publish shadow state so device gets marked as connected
        self._last_published_shadow_state = None
        self._config.sync_device_state()

    def _publish_legacy_telem(self, data: TelemData):
        # any value in the dict that is a list (or list of lists) must be converted to a string
        # before being sent to MQTT
        app_data = data.data
        for key, value in app_data.items():
            if isinstance(value, list):
                # Convert list to string
                app_data[key] = json.dumps(value)

        publish_data = {
            "data": app_data,
            "time_utc": data.utc_time_ms,
            "meta": {"build_id": data.build_id},
        }
        logger.debug("Publishing most recent app data: %s", publish_data)

        json_publish_data = json.dumps(publish_data)

        self._mqtt_connection.publish(
            topic=self._legacy_message_topic,
            payload=json_publish_data,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        self._last_legacy_persist_ms = data.utc_time_ms
