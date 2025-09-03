from .core import PostcardData
from .varint import UnsignedVarint, UnsignedVarintType


class StaticString(PostcardData):
    """
    Deserializes a static string from a Postcard byte stream.

    Strings are similar to arrays, but only contain UTF-8 encoded characters.
    """

    def __init__(self):
        super().__init__()

    def deserialize(self, bytes: bytearray) -> str:
        """
        Deserialize the given byte stream into a list of PostcardFlavor
        objects.
        """
        # First element is a usize that indicates the length of the array
        retval = []
        varint = UnsignedVarint(UnsignedVarintType.USIZE)
        size = varint.deserialize(bytes)
        for _ in range(size):
            retval.append(bytes.pop(0))

        return bytearray(retval).decode("utf-8")

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """
        Check if the given string is a valid PostcardString.
        """
        return "str" in schema_item

    @classmethod
    def get_type(cls, schema_item):
        return StaticString

    @classmethod
    def from_schema(cls, schema_item: str):
        return StaticString()
