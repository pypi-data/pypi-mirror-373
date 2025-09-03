from typing import Any, List

from pictorus.postcard.deserialize.float import Float
from .core import PostcardData, PostcardList
from .varint import (
    SignedVarint,
    UnsignedVarint,
    UnsignedVarintType,
)


class Vec(PostcardList):
    def __init__(self, inner: PostcardData):
        super().__init__(inner)

    def deserialize(self, bytes: bytearray) -> List[Any]:
        """
        Deserialize the given byte stream into a list of PostcardFlavor
        objects.
        """
        # First element is a usize that indicates the length of the array
        retval = []
        varint = UnsignedVarint(UnsignedVarintType.USIZE)
        size = varint.deserialize(bytes)

        element = self._inner
        for _ in range(size):
            deserialize_item = element.deserialize(bytes)
            retval.append(deserialize_item)

        return retval

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """
        Check if the given string is a valid PostcardString.
        """
        return "Vec" in schema_item

    @classmethod
    def from_schema(cls, schema_item: str) -> PostcardList:
        if not schema_item.startswith("Vec<") or not schema_item.endswith(">"):
            raise ValueError("String did not start with Vec<")

        datatype = None
        # get the type of the Vec
        string_type = schema_item.replace("Vec<", "").replace(">", "")
        if SignedVarint.is_type(string_type):
            datatype = SignedVarint.from_schema(string_type)
        elif UnsignedVarint.is_type(string_type):
            datatype = UnsignedVarint.from_schema(string_type)
        elif Float.is_type(string_type):
            datatype = Float.from_schema(string_type)

        if datatype is None:
            raise ValueError(f"Vec type {datatype} not recognized")

        vec = Vec(datatype)

        return vec
