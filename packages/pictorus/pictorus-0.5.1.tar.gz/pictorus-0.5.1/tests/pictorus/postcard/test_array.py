import pytest
from pictorus.postcard import (
    UnsignedVarintType,
    UnsignedVarint,
    SignedVarintType,
    SignedVarint,
    Array,
)


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x01", [1], Array(UnsignedVarint(UnsignedVarintType.U8), [1])),
        (b"\x01\x02", [1, 2], Array(UnsignedVarint(UnsignedVarintType.U8), [2])),
        (b"\x80\x01", [128], Array(UnsignedVarint(UnsignedVarintType.U16), [1])),
        (
            b"\x7e\x7f\xfe\xff\x03",
            [63, -64, 32767],
            Array(SignedVarint(SignedVarintType.I16), [3]),
        ),
        (
            b"\x80\x01\x80\x01",
            [[128], [128]],
            Array(UnsignedVarint(UnsignedVarintType.U16), [2, 1]),
        ),
    ],
)
def test_array(bytes_input, expected, varint_type):
    byte_stream = bytearray(bytes_input)
    values = varint_type.deserialize(byte_stream)
    assert len(byte_stream) == 0
    assert values == expected, f"Expected {expected}, got {values}"
