import pytest
from pictorus.postcard import (
    UnsignedVarintType,
    UnsignedVarint,
    SignedVarintType,
    SignedVarint,
    Option,
    Float,
    FloatType,
)


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x00", 0, UnsignedVarintType.U8),
        (b"\x01\x01", 1, UnsignedVarintType.U8),
        (b"\x01\x7f", 127, UnsignedVarintType.U8),
        (b"\x01\x80\x01", 128, UnsignedVarintType.U16),
        (b"\x01\xff\x01", 255, UnsignedVarintType.U16),
        (b"\x01\xff\x7f", 16383, UnsignedVarintType.U16),
        (b"\x01\x80\x80\x01", 16384, UnsignedVarintType.U16),
        (b"\x01\x81\x80\x01", 16385, UnsignedVarintType.U16),
        (b"\x01\xff\xff\x03", 65535, UnsignedVarintType.U16),
    ],
)
def test_varint_signed_option(bytes_input, expected, varint_type):
    option = Option(UnsignedVarint(varint_type))
    byte_stream = bytearray(bytes_input)
    retvalue = option.deserialize(byte_stream)
    if retvalue:
        assert retvalue == expected
        assert len(byte_stream) == 0


@pytest.mark.parametrize(
    "bytes_input, expected, varint_type",
    [
        (b"\x00", 0, SignedVarintType.I8),
        (b"\x01\x01", -1, SignedVarintType.I8),
        (b"\x01\x02", 1, SignedVarintType.I8),
        (b"\x01\x7e", 63, SignedVarintType.I8),
        (b"\x01\x7f", -64, SignedVarintType.I16),
        (b"\x01\x80\x01", 64, SignedVarintType.I16),
        (b"\x01\x81\x01", -65, SignedVarintType.I16),
        (b"\x01\xfe\xff\x03", 32767, SignedVarintType.I16),
        (b"\x01\xff\xff\x03", -32768, SignedVarintType.I16),
    ],
)
def test_varint_unsigned_option(bytes_input, expected, varint_type):
    option = Option(SignedVarint(varint_type))
    byte_stream = bytearray(bytes_input)
    retvalue = option.deserialize(byte_stream)
    if retvalue:
        assert retvalue == expected
        assert len(byte_stream) == 0


# same test as above, but for float f32
@pytest.mark.parametrize(
    "bytes_input, expected",
    [
        (b"\x01\x00\x00\x00\x00", 0.0),
        (b"\x01\x00\x00\x80\x3f", 1.0),
        (b"\x01\x00\x00\x80\xbf", -1.0),
        (b"\x01\x00\x00\x00\x40", 2.0),
        (b"\x01\x00\x00\x00\xc0", -2.0),
        (b"\x01\xc3\xf5\x48\x40", 3.14),
        (b"\x01\xc3\xf5\x48\xc0", -3.14),
        (b"\x01\x00\x00\x00\x3f", 0.5),
        (b"\x01\x00\x00\x00\xbf", -0.5),
        (b"\x01\x00\x00\xc8\x42", 100.0),
        (b"\x01\x00\x00\xc8\xc2", -100.0),
        (b"\x01\xac\xc5\x27\x37", 1e-5),
        (b"\x01\xac\xc5\x27\xb7", -1e-5),
        (b"\x01\x00\x20\xf1\x47", 123456.0),
        (b"\x01\x00\x20\xf1\xc7", -123456.0),
    ],
)
def test_float_f32_option(bytes_input, expected):
    option = Option(Float(FloatType.F32))
    byte_stream = bytearray(bytes_input)
    float_value = option.deserialize(byte_stream)
    if float_value is not None:
        assert float_value == pytest.approx(
            expected
        ), f"Failed for input {bytes_input.hex()} (got {float_value})"
        assert len(byte_stream) == 0
