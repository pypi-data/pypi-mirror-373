# Schema

Schema are used to define the structure of the Postcard bytestreams that Python will deserialize. Currently the only schema support is JSON, which:
- Accepts a JSON representation of a Rust struct
- Creates a set of deserialization instructions
- Deserializes the Postcard bytestream according to the instructions
- Places the deserialized data into a Python `Dict` object with the keys being the field names and the values being the deserialized data.

For example, the following JSON schema:
```json
{
    "field_name": "u32",
    "field_name2": "Option<u64>"
}
```

would create a set of 3 instructions:
1. Deserialize a `u32` and place it in the `field_name` key.
2. Deserialize an `Option`, as it may be `Some` or `None`.
3. Deserialize the inner `Option` value, which is a `u64`, and place it in the `field_name2` key.
Every time `convert` is called, the list of instructions is executed in order on the incoming bytestream, and the results are placed in a Python dictionary.