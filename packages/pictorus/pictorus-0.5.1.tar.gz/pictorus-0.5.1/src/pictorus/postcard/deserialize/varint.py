from enum import Enum
from .core import PostcardData

MAX_U8 = 2**8 - 1
MAX_U16 = 2**16 - 1
MAX_U32 = 2**32 - 1
MAX_U64 = 2**64 - 1
MAX_U128 = 2**128 - 1

MIN_I8 = -(2**7)
MAX_I8 = 2**7 - 1
MIN_I16 = -(2**15)
MAX_I16 = 2**15 - 1
MIN_I32 = -(2**31)
MAX_I32 = 2**31 - 1
MIN_I64 = -(2**63)
MAX_I64 = 2**63 - 1
MIN_I128 = -(2**127)
MAX_I128 = 2**127 - 1

MAX_BYTES = 16


class UnsignedVarintEnum(Enum):
    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    USIZE = "usize"
    U64 = "u64"
    U128 = "u128"


UNSIGNED_VARINTS = [
    UnsignedVarintEnum.U8.value,
    UnsignedVarintEnum.U16.value,
    UnsignedVarintEnum.U32.value,
    UnsignedVarintEnum.USIZE.value,
    UnsignedVarintEnum.U64.value,
    UnsignedVarintEnum.U128.value,
]


class UnsignedVarintType(Enum):
    U8 = (UnsignedVarintEnum.U8.value, 0, MAX_U8)
    U16 = (UnsignedVarintEnum.U16.value, 0, MAX_U16)
    U32 = (UnsignedVarintEnum.U32.value, 0, MAX_U32)
    USIZE = (UnsignedVarintEnum.USIZE.value, 0, MAX_U32)  # Assuming usize for ARM Cortex-M4
    U64 = (UnsignedVarintEnum.U64.value, 0, MAX_U64)
    U128 = (UnsignedVarintEnum.U128.value, 0, MAX_U128)

    @property
    def min(self) -> int:
        return self.value[1]

    @property
    def max(self) -> int:
        return self.value[2]

    @property
    def name(self) -> str:
        return self.value[0]


class SignedVarintEnum(Enum):
    I8 = "i8"
    I16 = "i16"
    I32 = "i32"
    ISIZE = "isize"
    I64 = "i64"
    I128 = "i128"


SIGNED_VARINTS = [
    SignedVarintEnum.I8.value,
    SignedVarintEnum.I16.value,
    SignedVarintEnum.I32.value,
    SignedVarintEnum.ISIZE.value,
    SignedVarintEnum.I64.value,
    SignedVarintEnum.I128.value,
]


class SignedVarintType(Enum):
    I8 = (SignedVarintEnum.I8.value, MIN_I8, MAX_I8)
    I16 = (SignedVarintEnum.I16.value, MIN_I16, MAX_I16)
    I32 = (SignedVarintEnum.I32.value, MIN_I32, MAX_I32)
    ISIZE = (SignedVarintEnum.ISIZE.value, MIN_I32, MAX_I32)  # Assuming isize for ARM Cortex-M4
    I64 = (SignedVarintEnum.I64.value, MIN_I64, MAX_I64)
    I128 = (SignedVarintEnum.I128.value, MIN_I128, MAX_I128)

    @property
    def min(self) -> int:
        return self.value[1]

    @property
    def max(self) -> int:
        return self.value[2]

    @property
    def name(self) -> str:
        return self.value[0]


class UnsignedVarint(PostcardData):
    """
    Deserializes unsigned variable-length integers.

    See
    https://postcard.jamesmunns.com/wire-format
    or
    https://protobuf.dev/programming-guides/encoding/

    for more information.

    UnsignedVarint is used as the basis for SignedVarint.
    """

    def __init__(self, type: UnsignedVarintType):
        super().__init__()
        self.starts_with = "u8, u16, u32, usize, u64, u128"
        self._type = type

    @classmethod
    def from_schema(cls, schema_item):
        return UnsignedVarint(cls.get_type(schema_item))

    def deserialize(self, bytes: bytearray) -> int:
        """
        Deserialize the varint bytes into an integer.
        """
        result = 0
        shift = 0

        if self._type == UnsignedVarintType.U8:
            # Postcard doesn't encode U8, I8 as varint, so just
            # pop the first byte and return it.
            return bytes.pop(0)

        # Start popping bytes from the front of the byte array up to
        # 16 bytes. If the loop finishes before 16 bytes, break.
        for _ in range(MAX_BYTES):
            if len(bytes) == 0:
                return result  # No more data to deserialize, return what we have

            # Deserialize and accumulate the shift, checking the most significant
            # bit to see if we need to continue.
            byte = bytes.pop(0)
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7

        # Check the result against the type's range.
        if self._type.value[1] <= result <= self._type.value[2]:
            return result

        raise ValueError(f"Value {result} is out of range for type {self._type.value[0]}")

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        """
        Check if the given string matches the unsigned varint type.
        """
        return schema_item in UNSIGNED_VARINTS

    @classmethod
    def get_type(cls, schema_item: str) -> UnsignedVarintType:
        """
        Get the UnsignedVarintType from a string.
        """
        if schema_item == UnsignedVarintEnum.U8.value:
            return UnsignedVarintType.U8
        elif schema_item == UnsignedVarintEnum.U16.value:
            return UnsignedVarintType.U16
        elif schema_item == UnsignedVarintEnum.U32.value:
            return UnsignedVarintType.U32
        elif schema_item == UnsignedVarintEnum.USIZE.value:
            return UnsignedVarintType.USIZE
        elif schema_item == UnsignedVarintEnum.U64.value:
            return UnsignedVarintType.U64
        elif schema_item == UnsignedVarintEnum.U128.value:
            return UnsignedVarintType.U128
        else:
            raise ValueError(f"Could not parse {schema_item} as a UnsignedVarintType")


class SignedVarint(PostcardData):
    """
    Uses an UnsignedVarint + zigzag decoding to deserialize signed integers.
    """

    def __init__(self, type: SignedVarintType):
        super().__init__()
        self.starts_with = "i8, i16, i32, isize, i64, i128"
        self._type = type

    def _zigzag_decode(self, n: int) -> int:
        # Pretty good explanation of zigzag encoding:
        # https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
        return (n >> 1) ^ -(n & 1)

    def _get_signed_type(self) -> UnsignedVarintType:
        """
        Get the corresponding unsigned varint type for the signed varint type.
        """
        if self._type == SignedVarintType.I8:
            return UnsignedVarintType.U8
        elif self._type == SignedVarintType.I16:
            return UnsignedVarintType.U16
        elif self._type == SignedVarintType.I32 or self._type == SignedVarintType.ISIZE:
            return UnsignedVarintType.U32
        elif self._type == SignedVarintType.I64:
            return UnsignedVarintType.U64
        elif self._type == SignedVarintType.I128:
            return UnsignedVarintType.U128
        else:
            raise ValueError(f"Unsupported signed varint type: {self._type}")

    def deserialize(self, bytes: bytearray) -> int:
        # Deserialize as an UnsignedVarint
        unsigned = UnsignedVarint(self._get_signed_type()).deserialize(bytes)

        result = self._zigzag_decode(unsigned)

        # Check if the result is within the range of the signed varint type
        if self._type.value[1] <= result <= self._type.value[2]:
            return result

        raise ValueError((f"Value {result} is out of range " f"for type" f" {self._type.value[0]}"))

    @classmethod
    def is_type(cls, schema_item: str) -> bool:
        return schema_item in SIGNED_VARINTS

    @classmethod
    def from_schema(cls, schema_item):
        return SignedVarint(cls.get_type(schema_item))

    @classmethod
    def get_type(cls, schema_item: str) -> SignedVarintType:
        if schema_item == SignedVarintType.I8.value:
            return SignedVarintType.I8
        elif schema_item == SignedVarintEnum.I16.value:
            return SignedVarintType.I16
        elif schema_item == SignedVarintEnum.I32.value:
            return SignedVarintType.I32
        elif schema_item == SignedVarintEnum.ISIZE.value:
            return SignedVarintType.ISIZE
        elif schema_item == SignedVarintEnum.I64.value:
            return SignedVarintType.I64
        elif schema_item == SignedVarintEnum.I128.value:
            return SignedVarintType.I128
        else:
            raise ValueError(f"Could not parse {schema_item} as a SignedVarintType")
