import pytest
from pictorus.postcard import (
    UnsignedVarintType,
    UnsignedVarint,
    Vec,
)


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x01\x01", [1], Vec(UnsignedVarint(UnsignedVarintType.U8))),
        (b"\x02\x01\x02", [1, 2], Vec(UnsignedVarint(UnsignedVarintType.U8))),
    ],
)
def test_array(bytes_input, expected, varint_type):
    byte_stream = bytearray(bytes_input)
    values = varint_type.deserialize(byte_stream)
    assert len(byte_stream) == 0
    assert values == expected, f"Expected {expected}, got {values}"
