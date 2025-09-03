from typing import Any, List

from pictorus.postcard.deserialize.float import Float
from pictorus.postcard.deserialize.varint import SignedVarint, UnsignedVarint
from .core import PostcardData, PostcardList


class Array(PostcardList):
    """
    Represents a statically allocated array, which does not have a length prefix like
    a Vec. This requires a determining the dimensions of the array from the Rust
    type string, such as [f32; 4] or [[f32; 4]; 2].
    """

    def __init__(self, inner: PostcardData, dims: List[int]):
        super().__init__(inner=inner)
        self._dims = dims

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """Check if the schema entry is of this PostcardItem type."""
        return schema_item.startswith("[") and schema_item.endswith("]")

    def _reshape_1d_to_2d_loop(self, arr, rows, cols):
        """
        Reshape a 1D array into a 2D array based on the specified rows and columns.

        The statically allocated arrays come across as a flat list and need to
        be reshaped to match the Rust array dimensions.
        """
        if len(arr) != rows * cols:
            raise ValueError("Incompatible dimensions for reshaping.")

        result = []
        for i in range(0, len(arr), cols):
            result.append(arr[i : i + cols])
        return result

    def deserialize(self, bytes: bytearray) -> List[Any]:
        """
        Deserialize the given byte stream into a list of PostcardFlavor
        objects.
        """
        if self._dims is None:
            raise ValueError("Array dimensions have not been set. Use set_dims() before decoding.")

        # Arrays don't have a length prefix, so we need to use the
        # _dims member.
        retval = []
        elements = 1
        for dim in self._dims:
            elements *= dim

        element = self._inner
        for _ in range(elements):
            # If the element is PostcardData, we can deserialize it directly
            deserialized_item = element.deserialize(bytes)
            retval.append(deserialized_item)

        if len(self._dims) == 2:
            retval = self._reshape_1d_to_2d_loop(
                retval, self._dims[0], self._dims[1] if len(self._dims) > 1 else 1
            )

        return retval

    @classmethod
    def from_schema(cls, schema_item: str) -> PostcardList:
        """
        Splits a 1D or 2D array into a PostcardList objects or the type.

        For example, [f32; 4] becomes Array([Float(FloatType.F32)]), and would
        deserialize as a float array of length 4.

        [[f32; 4]; 2] becomes
        Array([Array(Float(FloatType.F32)), Array(Float(FloatType.F32))])
        which is a 2D array of floats, with each inner decoding as a float array.
        """
        if schema_item[0] != "[":
            raise ValueError("String did not start with a [")

        splits = schema_item.split(";")

        if len(splits) < 2:
            raise ValueError(("Couldn't split string, maybe missing a semicolon ';' ?"))
        else:
            datatype = None
            # get the type of the array
            last_open_bracket = splits[0].rfind("[") + 1
            string_type = splits[0][last_open_bracket:]
            if SignedVarint.is_type(string_type):
                datatype = SignedVarint.from_schema(string_type)
            elif UnsignedVarint.is_type(string_type):
                datatype = UnsignedVarint.from_schema(string_type)
            elif Float.is_type(string_type):
                datatype = Float.from_schema(string_type)

            if datatype is None:
                raise ValueError(f"Array type {datatype} not recognized")

            dims = []
            for i in range(1, len(splits)):
                closing_bracket = splits[i].find("]")
                array_count = int(splits[i][:closing_bracket])
                dims.append(array_count)

            if len(dims) > 2:
                raise ValueError(
                    "Only 1D and 2D arrays are supported, " f"got {len(dims)} dimensions."
                )

            # swap rows and columns
            dims.reverse()

            return Array(datatype, dims)
