import pytest
from pictorus.postcard import Float, FloatType


@pytest.mark.parametrize(
    "bytes_input, expected",
    [
        (b"\x00\x00\x00\x00", 0.0),
        (b"\x00\x00\x80\x3f", 1.0),
        (b"\x00\x00\x80\xbf", -1.0),
        (b"\x00\x00\x00\x40", 2.0),
        (b"\x00\x00\x00\xc0", -2.0),
        (b"\xc3\xf5\x48\x40", 3.14),
        (b"\xc3\xf5\x48\xc0", -3.14),
        (b"\x00\x00\x00\x3f", 0.5),
        (b"\x00\x00\x00\xbf", -0.5),
        (b"\x00\x00\xc8\x42", 100.0),
        (b"\x00\x00\xc8\xc2", -100.0),
        (b"\xac\xc5\x27\x37", 1e-5),
        (b"\xac\xc5\x27\xb7", -1e-5),
        (b"\x00\x20\xf1\x47", 123456.0),
        (b"\x00\x20\xf1\xc7", -123456.0),
    ],
)
def test_float_f32_deserialize(bytes_input, expected):
    float_value = Float(FloatType.F32)
    byte_stream = bytearray(bytes_input)
    deserialized = float_value.deserialize(byte_stream)
    assert deserialized == pytest.approx(
        expected
    ), f"Failed for input {bytes_input.hex()} (got {deserialized})"
    assert len(byte_stream) == 0  # Ensure all bytes were consumed
