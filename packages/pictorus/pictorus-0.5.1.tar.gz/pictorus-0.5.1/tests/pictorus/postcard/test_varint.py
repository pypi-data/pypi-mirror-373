import pytest
from pictorus.postcard import UnsignedVarintType, UnsignedVarint, SignedVarintType, SignedVarint


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x01", 1, UnsignedVarintType.U8),
        (b"\x02", 2, UnsignedVarintType.U8),
        (b"\x7f", 127, UnsignedVarintType.U8),
        (b"\x80", 128, UnsignedVarintType.U8),
        (b"\xff", 255, UnsignedVarintType.U8),
        (b"\x7f", 127, UnsignedVarintType.U16),
        (b"\x80\x01", 128, UnsignedVarintType.U16),
        (b"\xff\x7f", 16383, UnsignedVarintType.U16),
        (b"\x80\x80\x01", 16384, UnsignedVarintType.U16),
        (b"\x81\x80\x01", 16385, UnsignedVarintType.U16),
        (b"\xff\xff\x03", 65535, UnsignedVarintType.U16),
    ],
)
def test_varint_unsigned_deserialize(bytes_input, expected, varint_type):
    varint = UnsignedVarint(varint_type)
    byte_stream = bytearray(bytes_input)
    assert (
        varint.deserialize(byte_stream) == expected
    ), f"Failed for input {expected} for type {varint_type}"
    # Ensure all bytes were consumed
    assert len(byte_stream) == 0, f"Failed for input {expected}"


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x00", 0, SignedVarintType.I16),
        (b"\x01", -1, SignedVarintType.I16),
        (b"\x02", 1, SignedVarintType.I16),
        (b"\x7e", 63, SignedVarintType.I16),
        (b"\x7f", -64, SignedVarintType.I16),
        (b"\x80\x01", 64, SignedVarintType.I16),
        (b"\x81\x01", -65, SignedVarintType.I16),
        (b"\xfe\xff\x03", 32767, SignedVarintType.I16),
        (b"\xff\xff\x03", -32768, SignedVarintType.I16),
    ],
)
def test_varint_signed_deserialize(bytes_input, expected, varint_type):
    varint = SignedVarint(varint_type)
    byte_stream = bytearray(bytes_input)
    assert varint.deserialize(byte_stream) == expected, f"Failed for input {expected}"
    # Ensure all bytes were consumed
    assert len(byte_stream) == 0, f"Failed for input {expected}"
