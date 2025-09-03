# Deserializer

Deserializers are responsible for converting Postcard Serialized data into a Python object. A Deserializer should implement the `deserialize` method for the particular Postcard object that it represents.

There are three types of deserialize classes defined:
- **PostcardData** Represents a Rust data type, such as `u32`, `f64`, etc.
- **PostcardList** Represents a Rust array data, such as `[u32; 4]`, `[[f64; 2]; 3]` or a `Vec`, etc.
- **PostcardContainer** Represents a Rust object that can contain an inner object, for example an `Option` that can contain a single value, a `Vec` or even another `Option`. 

Pictorus currently uses a limited subset of the Postcard protocol:
- Varint types (u8, u16, u32, usize, u64, u128, i8, i16, i32, isize, i64, i128)
- Floats (f32, f64)
- Statically allocated Arrays (1D and 2D currently, only Varint and Float)
- Options
- Strings
- Vectors (varint and Float types)

So deserializers are implemented for these types.