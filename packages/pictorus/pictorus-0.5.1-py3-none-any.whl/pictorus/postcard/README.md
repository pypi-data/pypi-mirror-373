# Postcard Bytestream Deserialize

# Overview
This project is a Python implementation of a deserializer for the Rust Postcard wire format, which is used in the Postcard protocol for sending and receiving data. The deserializer is designed to handle various data types and structures as defined in the Postcard specification.

See the [Postcard Wire Format](https://postcard.jamesmunns.com/wire-format) for more information about the Postcard protocol.

# Why?
We need a way to deserialize Postcard bytestreams dynamically where the struct can be different from one device to the next. Wrapping the Rust struct and exporting it to Python or using bindgen to create a Python library doesn't work because each device has specific struct that changes program to program.

# Features
- Describe a Rust struct in JSON format and dynamically deserialize the Postcard bytestream from the JSON description.
- Supports:
    - Varint types (u8, u16, u32, usize, u64, u128, i8, i16, i32, iszie, i64, i128)
    - Floats (f32, f64)
    - Statically allocated Arrays (1D and 2D currently, only Varint and Float types are supported)
    - Options
    - Strings
    - Vectors (varint and Float types)
- Outputs the deserialize data as a JSON object.

# Usage
To use the Postcard bytestream deserialize package, follow these steps:
1. Create a `JsonSchema` object. This is a JSON representation of a Rust struct. The constructor accepts a dictionary that describes the structure of the data you want to deserialize. For example:
    ```python
    from pictorus.postcard.schema import JsonSchema

    schema = {
        "field_name": "u32",
        "field_name2": "Option<u64>"
    }
    json_schema = JsonSchema(schema)
    ```
1. Use the `convert` method to deserialize a Postcard bytestream:
    ```python
    data = b'\x01\x02\x03...'  # Your Postcard bytestream
    deserialized_data = json_schema.convert(data)
    print(deserialized_data)  # Outputs the deserialized data as a JSON object
    ```
    This will loop through the instructions and deserialize the data according to the structure defined by the JSON dictionary used in the constructor. It can be re-used for multiple streams of the same type.

# Tips
- Make sure to account for COBS encoding if your Postcard bytestream is COBS encoded. You can use the `cobs` library to decode it before passing it to the `convert` method.

