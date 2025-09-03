from subprocess import PIPE, STDOUT
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch, Mock, mock_open
import threading
import json

import pytest
import responses

from pictorus.comms.comms_handler import TelemData
from pictorus.constants import EMPTY_ERROR
from pictorus.exceptions import CommandError
from pictorus.target_manager.target_manager import TargetMgrConfig
from pictorus.target_manager.proc_target_manager import ProcTargetManager
from pictorus.command import DeployTarget, Command, CmdType
from pictorus.config import Config
from pictorus.types import AppLogLevel, LogMessage, TargetState
from ...utils import (
    expected_assets_dir,
    expected_bin_path,
    expected_error_log_path,
    wait_for_condition,
    setup_update_cmd,
)
import cobs.cobs


ADDR_DATA = ("127.0.0.1", 1234)
LOG_LINES = [
    b"2023-01-01T00:00:00.000Z [INFO] - foo",
    b"2023-01-01T00:00:01.000Z [WARN] - bar",
    b"2023-01-01T00:00:02.000Z [DEBUG] - baz",
    b"Nonsense",
]
global_config = Config()


def _assert_correct_app_start(
    mgr: ProcTargetManager, m_popen: Mock, target_id: str, log_level=AppLogLevel.INFO
):
    m_popen.assert_called_once_with(
        expected_bin_path(target_id),
        stdout=PIPE,
        stderr=STDOUT,
        env={
            "APP_PUBLISH_SOCKET": f"{ADDR_DATA[0]}:{ADDR_DATA[1]}",
            "APP_RUN_PATH": expected_assets_dir(target_id),
            "LOG_LEVEL": log_level.value,
        },
    )

    assert mgr._telem_listener_thread is not None
    assert mgr._telem_listener_thread.is_alive() is True

    assert mgr._logging_thread is not None
    # TODO: We currently mock the log behavior so the log thread will terminate immediately
    # assert mgr._logging_thread.is_alive() is True


def _assert_correct_app_stop(mgr: ProcTargetManager, m_popen: Mock):
    m_popen.assert_not_called()
    m_popen.return_value.terminate.assert_called_once()


def _mock_popen(m_popen: Mock):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0
    m_popen.return_value = mock_proc


@patch("pictorus.target_manager.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.target_manager.os.chmod", new=Mock())
@patch("pictorus.target_manager.proc_target_manager._path_exists", return_value=True)
@patch("pictorus.target_manager.proc_target_manager.Popen")
class TestProcTargetManager(TestCase):
    BUILD_HASH = "abc123"
    TARGET_ID = "foo"
    TARGET = DeployTarget({"id": TARGET_ID, "type": "process"})

    def setUp(self) -> None:
        socket_patch = patch("pictorus.target_manager.proc_target_manager.socket.socket")
        m_socket = socket_patch.start()
        self.mock_socket = MagicMock()
        self.mock_socket.getsockname.return_value = ADDR_DATA
        self.mock_socket.recv.return_value = b""
        m_socket.return_value.__enter__.return_value = self.mock_socket
        self.addCleanup(socket_patch.stop)

        return super().setUp()

    def test_starts_app_on_entry(self, m_popen, _):
        _mock_popen(m_popen)
        target_state = TargetState(run_app=True, build_hash=self.BUILD_HASH)
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config) as mgr:
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

        m_popen.return_value.terminate.assert_called_once()

    def test_does_not_start_app_on_entry(self, m_popen, _):
        target_state = TargetState(run_app=False, build_hash=self.BUILD_HASH)
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config):
            m_popen.assert_not_called()

        m_popen.return_value.terminate.assert_not_called()

    def test_starts_and_stops_app(self, m_popen, _):
        _mock_popen(m_popen)
        target_state = TargetState(run_app=False, build_hash=self.BUILD_HASH)
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config) as mgr:
            # Start the app
            start_app_cmd = Command(
                id="1",
                type=CmdType.RUN_APP,
                data={"run_app": True},
                target_id=self.TARGET_ID,
            )
            m_popen.reset_mock()
            mgr.handle_command(start_app_cmd)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

            # Calling start again should do nothing
            m_popen.reset_mock()
            mgr.handle_command(start_app_cmd)
            m_popen.assert_not_called()

            # Stop the app
            stop_app_cmd = Command(
                id="2",
                type=CmdType.RUN_APP,
                data={"run_app": False},
                target_id=self.TARGET_ID,
            )
            m_popen.reset_mock()
            mgr.handle_command(stop_app_cmd)
            _assert_correct_app_stop(mgr, m_popen)

    @responses.activate
    def test_starts_app_on_update(self, m_popen, _):
        _mock_popen(m_popen)
        new_build_id = "newfoo"
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="http://foo.bar/params.json",
            build_id=new_build_id,
            params_hash="newparams123",
            target_data=self.TARGET.to_dict(),
        )

        target_state = TargetState(run_app=True, build_hash=self.BUILD_HASH)
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with patch("builtins.open"), ProcTargetManager(config) as mgr:
            m_popen.reset_mock()

            mgr.handle_command(update_app_cmd)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

            expected_target_state.run_app = True
            assert mgr.target_state == expected_target_state

    def test_set_log_level(self, m_popen, __):
        _mock_popen(m_popen)
        log_level = AppLogLevel.DEBUG
        set_ttl_cmd = Command(
            id="1",
            type=CmdType.SET_LOG_LEVEL,
            data={"log_level": log_level.value},
            target_id=self.TARGET_ID,
        )

        target_state = TargetState(run_app=True, build_hash=self.BUILD_HASH)
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config) as mgr:
            m_popen.reset_mock()
            mgr.handle_command(set_ttl_cmd)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID, log_level=log_level)

    @patch("pictorus.target_manager.proc_target_manager.os.remove")
    def test_sets_error_from_file_on_unexpected_crash(self, m_remove, m_popen, __):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        expected_err = {"err_type": "Foo", "message": "Bar"}
        target_state = TargetState(run_app=True, build_hash=self.BUILD_HASH)
        m_sync_cb = Mock()
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=m_sync_cb,
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config) as mgr, patch(
            "builtins.open", mock_open(read_data=json.dumps(expected_err))
        ):
            # Error should get cleared on init
            wait_for_condition(lambda: m_sync_cb.call_count == 1)
            assert mgr.target_state.error_log and mgr.target_state.error_log == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_called_once_with(expected_error_log_path(self.TARGET_ID))
        assert m_sync_cb.call_count == 2
        assert mgr.target_state.error_log == expected_err

    @patch("pictorus.target_manager.proc_target_manager.os.remove")
    def test_sets_default_error_on_unexpected_crash(self, m_remove, m_popen, m_exists):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        m_exists.side_effect = lambda p: p != expected_error_log_path(self.TARGET_ID)

        target_state = TargetState(run_app=True, build_hash=self.BUILD_HASH)
        m_sync_cb = Mock()
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=m_sync_cb,
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        with ProcTargetManager(config) as mgr:
            # Error should get cleared on init
            wait_for_condition(lambda: m_sync_cb.call_count == 1)
            assert mgr.target_state.error_log and mgr.target_state.error_log == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_not_called()
        assert m_sync_cb.call_count == 2
        assert mgr.target_state.error_log == ProcTargetManager.NO_LOG_ERROR

    def test_test_no_telemetry_schema(self, _, __):
        target_state = TargetState(run_app=False, build_hash=self.BUILD_HASH)

        m_add_telem_cb = Mock()
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=m_add_telem_cb,
        )

        m_postcard_schema = {}

        mgr = ProcTargetManager(config)
        mgr._ready.wait(timeout=1)

        m_open = mock_open(read_data=json.dumps(m_postcard_schema))

        # Patch postcard params to deserialize the telemetry data
        with patch("builtins.open", m_open), patch(
            "pictorus.target_manager.proc_target_manager.os.path.exists", return_value=True
        ), pytest.raises(
            CommandError,
            match=(
                "Telemetry schema not found in parameters file."
                " Try re-compiling and deploying the app."
            ),
        ):
            mgr._start_listening()

    def test_listen_for_telem(self, _, __):
        target_state = TargetState(run_app=False, build_hash=self.BUILD_HASH)

        m_add_telem_cb = Mock()
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=m_add_telem_cb,
        )

        m_postcard_schema = {
            "app_time_us": "Option<u64>",
            "foo": "Option<u8>",
            "bar": "Option<Vec<u8>>",
        }

        mgr = ProcTargetManager(config)
        mgr._ready.wait(timeout=1)

        def mock_recv(*args, **kwargs):
            # Simulate a COBS-encoded byte stream with telemetry data of:
            # Option<u64> value 0
            # Option<u8> value 1
            # Option<Vec<u8>> values [1, 2]
            assert mgr._socket_data == ADDR_DATA
            # Hack to stop thread after one loop
            mgr._listen = False
            return cobs.cobs.encode(b"\x01\x00\x01\x01\x01\x02\x01\x02")

        self.mock_socket.recv.side_effect = mock_recv

        # Patch postcard params to deserialize the telemetry data
        with patch.object(mgr, "_load_telemetry_schema", return_value=m_postcard_schema):
            mgr._start_listening()
            wait_for_condition(lambda: m_add_telem_cb.call_count > 0)
            mgr.close()

        expected = TelemData(
            utc_time_ms=ANY,
            build_id=self.BUILD_HASH,
            data={
                "app_time_us": 0,
                "foo": 1,
                "bar": [1, 2],
            },
            target_id=self.TARGET_ID,
        )
        m_add_telem_cb.assert_called_once_with(expected)

        # Test changed schemas after a deploy event and ensure the new schema loads
        m_postcard_schema_other = {
            "app_time_us": "Option<u64>",
            "foo": "Option<f32>",
        }

        def recv_other(*args, **kwargs):
            # Simulate a COBS-encoded byte stream with telemetry data of:
            # Option<u64> value 0
            # Option<f32> value 1.0
            assert mgr._socket_data == ADDR_DATA
            # Hack to stop thread after one loop
            mgr._listen = False
            return cobs.cobs.encode(b"\x01\x00\x01\x00\x00\x80\x3f")

        self.mock_socket.recv.side_effect = recv_other

        # Patch postcard params to deserialize the telemetry data
        with patch.object(mgr, "_load_telemetry_schema", return_value=m_postcard_schema_other):
            mgr._start_listening()
            wait_for_condition(lambda: m_add_telem_cb.call_count > 1)
            mgr.close()

        expected = TelemData(
            utc_time_ms=ANY,
            build_id=self.BUILD_HASH,
            data={
                "app_time_us": 0,
                "foo": 1.0,
            },
            target_id=self.TARGET_ID,
        )

        m_add_telem_cb.assert_any_call(expected)

    def test_log_data(self, m_popen, _):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.stdout.readline.side_effect = LOG_LINES

        target_state = TargetState(run_app=False, build_hash=self.BUILD_HASH)
        m_add_logs_cb = Mock()
        config = TargetMgrConfig(
            target=self.TARGET,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=m_add_logs_cb,
            add_telem_cb=Mock(),
        )
        mgr = ProcTargetManager(config)
        mgr._listen = True
        mgr._start_logging(mock_proc)
        wait_for_condition(lambda: m_add_logs_cb.call_count == len(LOG_LINES))

        expected_payload = [
            LogMessage(
                timestamp=1672531200000,
                level="info",
                message="foo",
            ),
            LogMessage(
                timestamp=1672531201000,
                level="warning",
                message="bar",
            ),
            LogMessage(
                timestamp=1672531202000,
                level="debug",
                message="baz",
            ),
            LogMessage(
                timestamp=ANY,
                message="Nonsense",
            ),
        ]

        for log in expected_payload:
            m_add_logs_cb.assert_any_call(log, self.TARGET_ID)
