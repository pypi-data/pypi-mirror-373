from typing import Any, Union

from pictorus.postcard.deserialize.float import Float
from pictorus.postcard.deserialize.string import StaticString
from pictorus.postcard.deserialize.varint import SignedVarint, UnsignedVarint
from pictorus.postcard.deserialize.array import Array
from pictorus.postcard.deserialize.vec import Vec
from .core import PostcardData, PostcardContainer, PostcardList


class Option(PostcardContainer):
    """
    Option can contain None or Some supported Postcard type.

    An option is serialized as 0x00 for None (with no other data), or 0x01
    followed by the serialized data of the inner type.
    """

    def __init__(self, inner: Union[PostcardData, PostcardContainer, PostcardList]):
        super().__init__(inner=inner)

    def deserialize(self, bytes: bytearray) -> Any:
        byte = bytes.pop(0)
        if byte == 0:
            return None
        if byte == 1:
            return self._inner.deserialize(bytes)

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """
        Check if the instruction is an Option type.
        """
        return schema_item.startswith("Option<") and schema_item.endswith(">")

    @classmethod
    def from_schema(cls, schema_item: str) -> Union[PostcardContainer, PostcardData, PostcardList]:
        """
        Extract the type from an Option instruction.
        Currently supports:
        - string
        - integers
        - floats
        - Statically allocated arrays
        - Vecs of integer or float types
        """
        inner_type = schema_item[len("Option<") : -1]
        if SignedVarint.is_type(inner_type):
            return Option(SignedVarint.from_schema(inner_type))
        elif UnsignedVarint.is_type(inner_type):
            return Option(UnsignedVarint.from_schema(inner_type))
        elif Float.is_type(inner_type):
            return Option(Float.from_schema(inner_type))
        elif Array.is_type(inner_type):
            # Handle Array type
            return Option(Array.from_schema(inner_type))
        elif StaticString.is_type(inner_type):
            # Handle String type
            return Option(StaticString())
        elif Vec.is_type(inner_type):
            # Handle Byte Array type
            return Option(Vec.from_schema(inner_type))

        raise ValueError(f"Unsupported Option inner type: {inner_type}")
