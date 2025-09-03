from enum import Enum
import struct
from .core import PostcardData

MIN_F32 = -3.402823466e38
MAX_F32 = 3.402823466e38

MIN_F64 = -1.7976931348623157e308
MAX_F64 = 1.7976931348623157e308

FLOAT_TYPES = ["f32", "f64"]


class FloatType(Enum):
    F32 = ("f32", MIN_F32, MAX_F32)
    F64 = ("f64", MIN_F64, MAX_F64)

    @property
    def min(self) -> float:
        return self.value[1]

    @property
    def max(self) -> float:
        return self.value[2]

    @property
    def name(self) -> str:
        return self.value[0]


def is_f32(string: str) -> bool:
    return string == FloatType.F32.name


def is_f64(string: str) -> bool:
    return string == FloatType.F64.name


class Float(PostcardData):
    """
    Deserializes a float or double from a bytearray.
    Supports both f32 and f64 types.

    These are always stores as 4 bytes (f32) or 8 bytes (f64)
    in little-endian format.
    """

    def __init__(self, type: FloatType):
        super().__init__()
        self._type = type

    def deserialize(self, bytes: bytearray) -> float:
        """
        Takes the bytearray and deserializes it as little-endian float.
        """
        loop_count = 4 if self._type == FloatType.F32 else 8
        bytes_to_convert = bytearray()
        for _ in range(loop_count):
            if not bytes:
                raise ValueError(f"Not enough bytes to deserialize {self._type.name}")
            bytes_to_convert.append(bytes.pop(0))

        if self._type == FloatType.F32:
            result = struct.unpack("<f", bytes_to_convert)[0]
        else:
            result = struct.unpack("<d", bytes_to_convert)[0]

        if self._type.value[1] <= result <= self._type.value[2]:
            return result

        raise ValueError(f"Value {result} is out of range for type {self._type.value[0]}")

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """
        Check if the given string matches the float type.
        """
        return is_f32(schema_item) or is_f64(schema_item)

    @classmethod
    def get_type(cls, schema_item: str) -> FloatType:
        """
        Get the FloatType from a string.
        """
        if is_f32(schema_item):
            return FloatType.F32
        elif is_f64(schema_item):
            return FloatType.F64
        else:
            raise ValueError(f"Could not parse {schema_item} as a FloatType")

    @classmethod
    def from_schema(cls, schema_item: str):
        """
        Create a Float instance from a schema item.
        """
        float_type = cls.get_type(schema_item)
        return cls(float_type)
