import pytest
from pictorus.postcard import StaticString, Option


@pytest.mark.parametrize(
    "instructions",
    [
        (bytearray(b"\x0d" + "Hello, World!".encode()), "Hello, World!"),
    ],
)
def test_postcard_string_encode(instructions):
    postcard_string = StaticString()
    bytes = instructions[0]
    encoded_bytes = postcard_string.deserialize(bytes)
    assert encoded_bytes == instructions[1], f"Expected {instructions[0]}, got {encoded_bytes}"
    assert len(bytes) == 0


@pytest.mark.parametrize(
    "instructions",
    [
        (bytearray(b"\x01\x0d" + "Hello, World!".encode()), "Hello, World!"),
        (bytearray(b"\x00"), None),
    ],
)
def test_postcard_option_string_encode(instructions):
    postcard_string = StaticString()
    postcard_option = Option(postcard_string)
    bytes = instructions[0]
    encoded_bytes = postcard_option.deserialize(bytes)
    assert encoded_bytes == instructions[1], f"Expected {instructions[0]}, got {encoded_bytes}"
    assert len(bytes) == 0
