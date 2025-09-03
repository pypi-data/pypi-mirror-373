import pytest
from pictorus.postcard import JsonSchema


@pytest.mark.parametrize(
    "instructions",
    [
        (b"\x01\x00\x00\x00\x00", 0.0, {"foo": "Option<f32>"}),
        (
            (b"\x00\x00\x00\x00\xc3\xf5\x48\x40" b"\x00\x00\xc8\x42\xac\xc5\x27\xb7"),
            [0.0, 3.14, 100, -1e-5],
            {"bar": "[f32; 4]"},
        ),
        (
            (b"\x01\x00\x00\x00\x00\xc3\xf5\x48\x40" b"\x00\x00\xc8\x42\xac\xc5\x27\xb7"),
            [0.0, 3.14, 100, -1e-5],
            {
                "foo": "Option<[f32; 4]>",
            },
        ),
    ],
)
def test_float(instructions):
    json_deserializer = JsonSchema(instructions[2])
    byte_stream = bytearray(instructions[0])
    output = json_deserializer.convert(byte_stream)
    for key, _ in instructions[2].items():
        assert output[key] == pytest.approx(instructions[1])


@pytest.mark.parametrize(
    "instructions",
    [
        (b"\x80\x01\x80\x01", [[128], [128]], {"bar": "[[u16; 1]; 2]"}),
    ],
)
def test_2d_array(instructions):
    json_deserializer = JsonSchema(instructions[2])
    byte_stream = bytearray(instructions[0])
    output = json_deserializer.convert(byte_stream)
    for key, _ in instructions[2].items():
        assert output[key] == instructions[1]


@pytest.mark.parametrize(
    "instructions",
    [
        (b"\x0dHello, World!", "Hello, World!", {"foo": "&'static str"}),
        (b"\x01\x0dHello, World!", "Hello, World!", {"foo": "Option<&'static str>"}),
    ],
)
def test_strings(instructions):
    json_deserializer = JsonSchema(instructions[2])
    byte_stream = bytearray(instructions[0])
    output = json_deserializer.convert(byte_stream)
    for key, _ in instructions[2].items():
        assert output[key] == instructions[1]


@pytest.mark.parametrize(
    "instructions",
    [
        (
            (
                b"\x01\x0fmaindd203_state\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x01\x00\x00\x00\x00\x00\x00\x00\x00"
            ),
            {
                "state_id": "maindd203_state",
                "timestamp": 0,
                "app_time_us": 0,
                "sinewave1_dea6c.0": 0,
                "sinewave2_dea81.0": 0,
                "sinewave3_dea83.0": 0,
                "sinewave4_dea84.0": 0,
                "sinewave5_dea87.0": 0,
                "sinewave6_dea88.0": 0,
                "sinewave7_dea8b.0": 0,
                "sinewave8_dea8c.0": 0,
                "sinewave9_dea90.0": 0,
                "sinewave10_dea91.0": 0,
                "sinewave11_dea94.0": 0,
                "sinewave12_dea95.0": 0,
                "sinewave13_dea98.0": 0,
                "sinewave14_dea99.0": 0,
                "sinewave15_dea9c.0": 0,
                "sinewave16_dea9d.0": 0,
                "sinewave17_deaa1.0": 0,
                "sinewave18_deaa2.0": 0,
                "sinewave19_deaa5.0": 0,
                "sinewave20_deaa6.0": 0,
                "sinewave21_deaa9.0": 0,
                "sinewave22_deaaa.0": 0,
                "sinewave23_deaad.0": 0,
            },
            {
                "state_id": "Option<&'static str>",
                "timestamp": "Option<f64>",
                "app_time_us": "Option<u64>",
                "sinewave1_dea6c.0": "Option<f64>",
                "sinewave2_dea81.0": "Option<f64>",
                "sinewave3_dea83.0": "Option<f64>",
                "sinewave4_dea84.0": "Option<f64>",
                "sinewave5_dea87.0": "Option<f64>",
                "sinewave6_dea88.0": "Option<f64>",
                "sinewave7_dea8b.0": "Option<f64>",
                "sinewave8_dea8c.0": "Option<f64>",
                "sinewave9_dea90.0": "Option<f64>",
                "sinewave10_dea91.0": "Option<f64>",
                "sinewave11_dea94.0": "Option<f64>",
                "sinewave12_dea95.0": "Option<f64>",
                "sinewave13_dea98.0": "Option<f64>",
                "sinewave14_dea99.0": "Option<f64>",
                "sinewave15_dea9c.0": "Option<f64>",
                "sinewave16_dea9d.0": "Option<f64>",
                "sinewave17_deaa1.0": "Option<f64>",
                "sinewave18_deaa2.0": "Option<f64>",
                "sinewave19_deaa5.0": "Option<f64>",
                "sinewave20_deaa6.0": "Option<f64>",
                "sinewave21_deaa9.0": "Option<f64>",
                "sinewave22_deaaa.0": "Option<f64>",
                "sinewave23_deaad.0": "Option<f64>",
            },
        ),
        (
            (
                b"\x01\x0fmain28bd6_state\x01\x93\xfd\xf34`\x90\x84?\x01\xb9N"
                b"\x01\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00"
                b"@\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x10@"
                b"\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x18@"
                b"\x01\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c"
                b"\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1"
                b"\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90"
                b"\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x01\x0c\xf2\xa1\x8fI\x90\x84?"
                b"\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2"
                b"\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI"
                b"\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?\x0c\xf2\xa1\x8fI\x90\x84?"
            ),
            {
                "state_id": "main28bd6_state",
                "timestamp": 0.010041,
                "app_time_us": 10041,
                "constant1_28bc0_0": [[1, 2, 3], [4, 5, 6]],
                "vector_merge1_2183d_0": [
                    [
                        0.0100408,
                        0.0100408,
                        0.0100408,
                        0.0100408,
                        0.0100408,
                        0.0100408,
                        0.0100408,
                        0.0100408,
                    ]
                ],
                "vector_reshape1_21846_0": [
                    [0.0100408, 0.0100408, 0.0100408, 0.0100408],
                    [0.0100408, 0.0100408, 0.0100408, 0.0100408],
                ],
            },
            {
                "state_id": "Option<&'static str>",
                "timestamp": "Option<f64>",
                "app_time_us": "Option<u64>",
                "constant1_28bc0_0": "Option<[[f64; 3]; 2]>",
                "vector_merge1_2183d_0": "Option<[[f64; 8]; 1]>",
                "vector_reshape1_21846_0": "Option<[[f64; 4]; 2]>",
            },
        ),
    ],
)
def test_actual_data(instructions):
    json_deserializer = JsonSchema(instructions[2])
    byte_stream = bytearray(instructions[0])
    output = json_deserializer.convert(byte_stream)
    for key, value in instructions[1].items():
        if isinstance(value, list):
            # For 1D or 2D arrays, we need to check each row or use numpy
            for i, row in enumerate(value):
                assert output[key][i] == pytest.approx(row, rel=1e-5)
        else:
            # Hopefully the rest of the values work with approx
            assert output[key] == pytest.approx(value, rel=1e-5)
    assert len(byte_stream) == 0, "Not all bytes were consumed during decoding"
