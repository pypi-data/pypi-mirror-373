from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol


class TypeSignatureType(Enum):
    BASE = auto()
    STRUCT = auto()
    ENUM = auto()
    ITERABLE = auto()
    MAP = auto()


class TypeSignature(Protocol):
    def get_type(self) -> TypeSignatureType: ...
    def signature(self) -> str: ...


@dataclass(frozen=True, kw_only=True, slots=True)
class DescriptiveTypeSignature:
    type: TypeSignatureType
    sig: str

    def get_type(self) -> TypeSignatureType:
        return self.type

    def signature(self) -> str:
        return self.sig


@dataclass(frozen=True, kw_only=True, slots=True)
class IterableTypeSignature:
    name: str
    item_type: TypeSignature

    def get_type(self) -> TypeSignatureType:
        return TypeSignatureType.ITERABLE

    def signature(self) -> str:
        return f"{self.name}<{self.item_type.signature()}>"


@dataclass(frozen=True, kw_only=True, slots=True)
class MapTypeSignature:
    key_type: TypeSignature
    value_type: TypeSignature

    def get_type(self) -> TypeSignatureType:
        return TypeSignatureType.MAP

    def signature(self) -> str:
        return f"map<{self.key_type.signature()}, {self.value_type.signature()}>"
