from enum import Enum

from ._typesignature import TypeSignatureType


class ProtoTypeSignature(Enum):
    BOOL = "bool"
    INT32 = "int32"
    INT64 = "int64"
    UINT32 = "uint32"
    UINT64 = "uint64"
    SINT32 = "sint32"
    SINT64 = "sint64"
    FIXED32 = "fixed32"
    FIXED64 = "fixed64"
    SFIXED32 = "sfixed32"
    SFIXED64 = "sfixed64"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BYTES = "bytes"
    UNKNOWN = "unknown"

    def get_type(self) -> TypeSignatureType:
        return TypeSignatureType.BASE

    def signature(self) -> str:
        return self.value
