import json
from unittest import TestCase
from unittest.mock import ANY, MagicMock, mock_open, patch, Mock

import pytest
import responses

from pictorus.command import DeployTarget
from pictorus.comms.comms_handler import TelemData
from pictorus.exceptions import CommandError
from pictorus.target_manager.target_manager import TargetMgrConfig
from pictorus.target_manager.embedded_target_manager import EmbeddedTargetManager
from pictorus.config import Config
from pictorus.types import ErrorLog, LogMessage, TargetState
from ...utils import expected_bin_path, setup_update_cmd, wait_for_condition

import cobs.cobs

from pyocd.core.exceptions import ProbeError

LOG_LINES = [
    b"[INFO] - foo",
    b"[WARN] - bar",
    b"[DEBUG] - baz",
    b"Nonsense",
]
global_config = Config()


def basic_update_command(target_data: dict):
    return setup_update_cmd(
        version_url="http://foo.bar/baz",
        params_url="",
        build_id="newfoo",
        params_hash="",
        target_data=target_data,
    )


@patch("pictorus.target_manager.embedded_target_manager.ConnectHelper.choose_probe", new=Mock())
@patch("pictorus.target_manager.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.target_manager.os.chmod", new=Mock())
@patch("pictorus.target_manager.embedded_target_manager.EmbeddedTargetManager._start_app_with_rtt")
@patch(
    "pictorus.target_manager.embedded_target_manager.is_pack_target_available", return_value=True
)
@patch("pictorus.target_manager.embedded_target_manager.ConnectHelper.session_with_chosen_probe")
@patch("pictorus.target_manager.embedded_target_manager.FileProgrammer")
class TestEmbeddedTargetManager(TestCase):
    @responses.activate
    def test_successful_deploy(self, m_prog, m_session, _, m_start):
        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        config = TargetMgrConfig(
            target=DeployTarget(target_data),
            target_state=TargetState(),
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        target_mgr = EmbeddedTargetManager(config)
        with patch("builtins.open"):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state == expected_target_state
        m_start.assert_not_called()

    @responses.activate
    def test_failed_deploy_unconnected(self, m_prog, m_session, _, __):
        m_session.return_value = None

        ocd_target = "stm32f4disco"
        target_data = {"id": "foo", "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        config = TargetMgrConfig(
            target=DeployTarget(target_data),
            target_state=TargetState(),
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        target_mgr = EmbeddedTargetManager(config)
        with patch("builtins.open"), pytest.raises(CommandError):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.assert_not_called()

        expected_target_state.error_log = ErrorLog(
            err_type="TargetConnectionError",
            message="Failed to connect to target. Make sure it is connected and powered on.",
        )
        assert target_mgr.target_state == expected_target_state

    def test_test_no_telemetry_schema(self, _, __, ___, ____):
        build_hash = "abcdef"
        target_state = TargetState(run_app=False, build_hash=build_hash)

        target_id = "foo"
        ocd_target = "stm32f4disco"
        target = DeployTarget(
            {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        )
        add_logs_cb = Mock()
        add_telem_cb = Mock()
        config: TargetMgrConfig = TargetMgrConfig(
            target=target,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=add_logs_cb,
            add_telem_cb=add_telem_cb,
        )
        mgr = EmbeddedTargetManager(config)

        m_postcard_schema = {}

        m_open = mock_open(read_data=json.dumps(m_postcard_schema))

        mock_log_chan = MagicMock()
        mock_data_chan = MagicMock()

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
            mgr._start_rtt_listener(mock_data_chan, mock_log_chan)

    @responses.activate
    def test_failed_deploy_failed_flash(self, m_prog, m_session, _, __):
        m_prog.return_value.program.side_effect = ProbeError

        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        config = TargetMgrConfig(
            target=DeployTarget(target_data),
            target_state=TargetState(),
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        target_mgr = EmbeddedTargetManager(config)
        with patch("builtins.open"), pytest.raises(ProbeError):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        assert (
            m_session.call_count == 3
        )  # Three session attempts are made, an initial and 2 retries

        m_prog.return_value.program.assert_called_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert m_prog.return_value.program.call_count == 2  # Two flash attempts are made

        expected_target_state.error_log = ErrorLog(
            err_type="UnknownError",
            message=(
                "Command failed: Failed to deploy app after two attempts. "
                "Make sure the target is connected and powered on and/or"
                " try restarting the device manager."
            ),
        )
        assert target_mgr.target_state == expected_target_state

    @responses.activate
    def test_auto_selects_target_name(self, m_prog, m_session, _, __):
        ocd_target = "stm32f45678"
        target_id = "foo"
        # No OCD target specified in the target data
        target_data = {"id": target_id, "type": "embedded", "options": {}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        config = TargetMgrConfig(
            target=DeployTarget(target_data),
            target_state=TargetState(),
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        target_mgr = EmbeddedTargetManager(config)
        with patch("builtins.open"), patch(
            "pictorus.target_manager.embedded_target_manager.ConnectHelper.choose_probe"
        ) as m_probe:
            # Probe lookup returns a target name
            m_probe.return_value.associated_board_info.target = ocd_target
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state == expected_target_state

    @responses.activate
    def test_installs_missing_target(self, m_prog, m_session, m_target_avail, _):
        # Target is not installed
        m_target_avail.return_value = False

        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        config = TargetMgrConfig(
            target=DeployTarget(target_data),
            target_state=TargetState(),
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=Mock(),
            add_telem_cb=Mock(),
        )
        target_mgr = EmbeddedTargetManager(config)
        with patch("builtins.open"), patch(
            "pictorus.target_manager.embedded_target_manager.cp.Cache"
        ) as m_cache, patch("pictorus.target_manager.embedded_target_manager.futures.wait"):
            cache = m_cache.return_value
            cache.index = {ocd_target: "bar"}
            packs = ["baz"]
            cache.packs_for_devices.return_value = packs

            target_mgr.handle_command(update_app_cmd)
            cache.download_pack_list.assert_called_once_with(packs)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state == expected_target_state

    def test_listen_for_telemetry_and_logs(self, _, __, ___, ____):
        mock_data_chan = MagicMock()

        m_postcard_schema = {
            "app_time_us": "Option<u64>",
            "foo": "Option<u8>",
            "bar": "Option<Vec<u8>>",
        }

        def mock_data_read():
            # Simulate a COBS-encoded byte stream with telemetry data of:
            # Option<u64> value 0
            # Option<u8> value 1
            # Option<Vec<u8>> values [1, 2]
            return cobs.cobs.encode(b"\x01\x00\x01\x01\x01\x02\x01\x02")

        mock_data_chan.read.side_effect = mock_data_read

        mock_log_chan = MagicMock()
        is_first_call_logs = True

        def mock_log_read():
            nonlocal is_first_call_logs
            if is_first_call_logs:
                is_first_call_logs = False
                return b"\n".join(LOG_LINES)

            return b""

        mock_log_chan.read.side_effect = mock_log_read

        build_hash = "abcdef"
        target_state = TargetState(run_app=False, build_hash=build_hash)

        target_id = "foo"
        ocd_target = "stm32f4disco"
        target = DeployTarget(
            {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        )
        add_logs_cb = Mock()
        add_telem_cb = Mock()
        config: TargetMgrConfig = TargetMgrConfig(
            target=target,
            target_state=target_state,
            updates_mgr=Mock(),
            sync_device_state_cb=Mock(),
            add_log_cb=add_logs_cb,
            add_telem_cb=add_telem_cb,
        )
        mgr = EmbeddedTargetManager(config)

        # Patch postcard params to deserialize the telemetry data
        with patch.object(mgr, "_load_telemetry_schema", return_value=m_postcard_schema):
            mgr._start_rtt_listener(mock_data_chan, mock_log_chan)
            wait_for_condition(lambda: add_logs_cb.call_count > 0)
            mgr._stop_rtt_listener()

        expected_payload = [
            LogMessage(
                timestamp=ANY,
                level="info",
                message="foo",
            ),
            LogMessage(
                timestamp=ANY,
                level="warning",
                message="bar",
            ),
            LogMessage(
                timestamp=ANY,
                level="debug",
                message="baz",
            ),
            LogMessage(
                timestamp=ANY,
                message="Nonsense",
            ),
        ]

        for msg in expected_payload:
            add_logs_cb.assert_any_call(msg, target_id)

        add_telem_cb.assert_any_call(
            TelemData(
                utc_time_ms=ANY,
                build_id=build_hash,
                data={
                    "app_time_us": 0,
                    "foo": 1,
                    "bar": [1, 2],
                },
                target_id=target_id,
            )
        )

        # Test changed schemas after a deploy event and ensure the new schema loads
        m_postcard_schema_other = {
            "app_time_us": "Option<u64>",
            "foo": "Option<f32>",
        }

        def mock_data_read_other():
            # Simulate a COBS-encoded byte stream with telemetry data of:
            # Option<u64> value 0
            # Option<f32> value 1.0
            return cobs.cobs.encode(b"\x01\x00\x01\x00\x00\x80\x3f")

        mock_data_chan.read.side_effect = mock_data_read_other

        with patch.object(mgr, "_load_telemetry_schema", return_value=m_postcard_schema_other):
            mgr._start_rtt_listener(mock_data_chan, mock_log_chan)
            wait_for_condition(lambda: add_logs_cb.call_count > 0)
            mgr._stop_rtt_listener()

        for msg in expected_payload:
            add_logs_cb.assert_any_call(msg, target_id)

        add_telem_cb.assert_any_call(
            TelemData(
                utc_time_ms=ANY,
                build_id=build_hash,
                data={
                    "app_time_us": 0,
                    "foo": 1.0,
                },
                target_id=target_id,
            )
        )
