import pytest

from pictorus.command import Command, CmdType


def test_from_dict_valid_minimal():
    data = {"type": CmdType.RUN_APP.value, "data": {"run_app": True}, "target_id": "foo"}
    cmd = Command.from_dict(data)
    assert cmd.type == CmdType.RUN_APP
    assert cmd.data == {"run_app": True}
    assert cmd.target_id == "foo"
    assert cmd.id is None


def test_from_dict_valid_with_id_and_target_object():
    data = {
        "id": "123",
        "type": CmdType.UPDATE_APP.value,
        "data": {"foo": "bar"},
        "target": {"id": "bar", "type": "process"},
    }
    cmd = Command.from_dict(data)
    assert cmd.id == "123"
    assert cmd.type == CmdType.UPDATE_APP
    assert cmd.data == {"foo": "bar"}
    assert cmd.target_id == "bar"


def test_from_dict_missing_type():
    data = {"data": {"run_app": True}, "target_id": "foo"}
    with pytest.raises(ValueError, match="Invalid command: missing type or data"):
        Command.from_dict(data)


def test_from_dict_missing_data():
    data = {"type": CmdType.RUN_APP.value, "target_id": "foo"}
    with pytest.raises(ValueError, match="Invalid command: missing type or data"):
        Command.from_dict(data)


def test_from_dict_invalid_id_type():
    data = {"id": 123, "type": CmdType.RUN_APP.value, "data": {"run_app": True}, "target_id": "foo"}
    with pytest.raises(ValueError, match="Invalid command id: 123"):
        Command.from_dict(data)


def test_from_dict_invalid_data_type():
    data = {"type": CmdType.RUN_APP.value, "data": "not_a_dict", "target_id": "foo"}
    with pytest.raises(ValueError, match="Invalid command data"):
        Command.from_dict(data)


def test_from_dict_missing_target():
    data = {"type": CmdType.RUN_APP.value, "data": {"run_app": True}}
    with pytest.raises(ValueError, match="Invalid command: missing target_id"):
        Command.from_dict(data)


def test_from_dict_target_object_missing_id():
    data = {"type": CmdType.RUN_APP.value, "data": {"run_app": True}, "target": {}}
    with pytest.raises(ValueError, match="Invalid command: missing target_id"):
        Command.from_dict(data)
