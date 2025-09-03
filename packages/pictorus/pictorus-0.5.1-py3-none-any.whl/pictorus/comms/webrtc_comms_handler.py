import asyncio
from dataclasses import asdict, dataclass
from enum import Enum
import json
import threading
import time
from typing import Dict, List, Optional, Union

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from cbor2 import dumps as cbor_dumps

from pictorus.command import CmdType, Command, CommandResult, StatusCode
from pictorus.comms.comms_handler import CommsConfig
from pictorus.comms.streaming_comms_handler import StreamingCommsConfig, StreamingCommsHandler
from pictorus.constants import THREAD_SLEEP_TIME_S
from pictorus.types import DeviceState, LogMessage
from pictorus.logging_utils import get_logger

logger = get_logger()


class ChannelType(Enum):
    """Supported channel types for WebRTC communication"""

    LOGS = "logs"
    TELEMETRY = "telemetry"
    COMMANDS = "commands"


@dataclass
class PeerConnection:
    pc: RTCPeerConnection
    log_channel: Optional[RTCDataChannel] = None
    telem_channel: Optional[RTCDataChannel] = None
    cmd_channel: Optional[RTCDataChannel] = None
    target_id: Optional[str] = None


@dataclass
class RTCOfferData:
    offer: RTCSessionDescription
    session_id: str


class WebRtcCommsHandler(StreamingCommsHandler):
    TELEM_PUBLISH_INTERVAL_S = 0.1  # 10 Hz
    TELEM_BATCH_SIZE = 1000
    TELEM_MAX_QUEUE_SIZE = 10000

    LOG_PUBLISH_INTERVAL_S = 1  # 1 Hz
    LOG_BATCH_SIZE = 100
    LOG_MAX_QUEUE_SIZE = 1000

    def __init__(self, config: CommsConfig) -> None:
        streaming_config = StreamingCommsConfig(
            sync_device_state=config.sync_device_state,
            process_cmd=config.process_cmd,
            telem_publish_interval_s=self.TELEM_PUBLISH_INTERVAL_S,
            telem_batch_size=self.TELEM_BATCH_SIZE,
            telem_max_queue_size=self.TELEM_MAX_QUEUE_SIZE,
            log_publish_interval_s=self.LOG_PUBLISH_INTERVAL_S,
            log_batch_size=self.LOG_BATCH_SIZE,
            log_max_queue_size=self.LOG_MAX_QUEUE_SIZE,
        )

        super().__init__(streaming_config)

        self._peers: dict[str, PeerConnection] = {}

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        # This thread will run the asyncio event loop
        self._running = False
        self._thread: threading.Thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        wait_start = time.time()
        while not self._running:
            # Wait for the event loop to be initialized
            time.sleep(0.1)
            if time.time() - wait_start > 10:
                raise RuntimeError("Failed to start WebRTC event loop within 10 seconds")

    def update_device_state(
        self, reported_state: DeviceState, desired_state: Union[DeviceState, None] = None
    ):
        # We don't do anything with this yet
        logger.debug("Updating device state: %s", reported_state)

    def close(self):
        """
        Close the WebRTC connections.
        """
        super().close()
        for data in self._peers.values():
            self._run_coroutine(data.pc.close())

        self._peers.clear()
        if self._loop:
            self._loop.stop()

        logger.info("Closed all WebRTC connections.")

    def _run_event_loop(self):
        """
        Run the asyncio event loop in a separate thread.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._poll_publish_data())

        self._running = True
        try:
            self._loop.run_forever()
        except Exception as e:
            logger.error("Event loop error: %s", e)
        finally:
            self._running = False
            self._loop.close()

    async def _poll_publish_data(self):
        """
        Poll for data to publish in the event loop.
        """
        while self._running:
            self._check_publish_data()
            await asyncio.sleep(THREAD_SLEEP_TIME_S)

    def _run_coroutine(self, coroutine):
        """
        Run a coroutine in the event loop.
        """
        if not self._running or self._loop is None:
            raise RuntimeError("Event loop is not running")

        return asyncio.run_coroutine_threadsafe(coroutine, self._loop).result()

    def accept_offer(self, data: RTCOfferData) -> RTCSessionDescription:
        """
        Accepts an offer and returns an answer.
        """
        return self._run_coroutine(self._accept_offer(data))

    async def _accept_offer(self, data: RTCOfferData) -> RTCSessionDescription:
        """
        Accepts an offer and returns an answer.
        """
        pc = RTCPeerConnection()
        peer_id = data.session_id

        old_session = self._peers.pop(peer_id, None)
        if old_session:
            await old_session.pc.close()

        self._peers[peer_id] = PeerConnection(pc=pc)
        pc.add_listener("datachannel", lambda c: self._handle_data_channel_created(peer_id, c))
        pc.add_listener(
            "connectionstatechange", lambda: self._handle_connection_state_change(peer_id)
        )

        await pc.setRemoteDescription(data.offer)
        answer = await pc.createAnswer()
        if not answer:
            raise RuntimeError("Failed to create answer for WebRTC offer")

        await pc.setLocalDescription(answer)
        return RTCSessionDescription(
            sdp=pc.localDescription.sdp,
            type=pc.localDescription.type,
        )

    def _handle_cmd_message(self, peer_id: str, message: bytes):
        """
        Handle incoming command messages.
        """
        self._on_cmd_request(json.loads(message), stream_id=peer_id)

    def _handle_data_channel_created(self, peer_id: str, channel: RTCDataChannel):
        logger.info(f"DataChannel created: {channel.label}")

        try:
            channel_type = ChannelType(channel.label)
        except ValueError:
            logger.warning("Received unsupported channel type: %s", channel.label)
            return

        peer_conn = self._peers.get(peer_id)
        if not peer_conn:
            logger.warning("Received data channel for unknown peer connection")
            return

        if channel_type == ChannelType.LOGS:
            peer_conn.log_channel = channel
        elif channel_type == ChannelType.TELEMETRY:
            peer_conn.telem_channel = channel
        elif channel_type == ChannelType.COMMANDS:
            peer_conn.cmd_channel = channel
            channel.add_listener("message", lambda msg: self._handle_cmd_message(peer_id, msg))

    def _handle_connection_state_change(self, peer_id: str):
        """
        Handle changes in the connection state of a peer connection.
        """
        data = self._peers.get(peer_id)
        if not data:
            logger.warning("Connection state change for unknown peer connection")
            return

        if data.pc.connectionState in ["failed", "closed"]:
            self._peers.pop(peer_id, None)

    def _publish_cmd_result(self, result: CommandResult, stream_id: Union[str, None] = None):
        """
        Publish the command result to the command channel.
        """
        if not stream_id:
            logger.warning("No stream ID provided for command result publication")
            return

        peer_conn = self._peers.get(stream_id)
        if not peer_conn or not peer_conn.cmd_channel:
            logger.warning("No command channel available to publish result")
            return

        result_data = result.to_dict()
        peer_conn.cmd_channel.send(json.dumps(result_data))

    def _publish_logs(self, target_id: str, logs: List[LogMessage]):
        log_data = json.dumps(list(map(asdict, logs)))
        for peer_conn in self._peers.values():
            if peer_conn.log_channel and peer_conn.target_id == target_id:
                peer_conn.log_channel.send(log_data)

    def _publish_telemetry(self, target_id: str, data: Dict[str, List]):
        telem_data = cbor_dumps(data)
        for peer_conn in self._peers.values():
            if peer_conn.telem_channel and peer_conn.target_id == target_id:
                peer_conn.telem_channel.send(telem_data)

    def _process_internal_cmd(
        self, cmd: Command, stream_id: Union[str, None] = None
    ) -> CommandResult:
        status = StatusCode.ERROR
        # We reuse the SET_TELEMETRY_TTL command to set the target ID each peer is subscribed to
        # We probably don't actually need to use the TTL since we can detect when the peer
        # disconnects, but simplest for now to just set it anyway
        if cmd.type == CmdType.SET_TELEMETRY_TLL:
            ttl_s = cmd.data.get("ttl_s", 0)
            self.set_ttl(ttl_s, cmd.target_id)
            peer_conn = self._peers.get(stream_id) if stream_id else None
            if peer_conn:
                peer_conn.target_id = cmd.target_id
                status = StatusCode.SUCCESS

        return CommandResult(
            id=cmd.id,
            type=cmd.type,
            status=status,
        )
