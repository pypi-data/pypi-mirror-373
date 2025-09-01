from collections.abc import Mapping, Sequence
from typing import TypeAlias

JSON: TypeAlias = (
    Mapping[str, "JSON"] | Sequence["JSON"] | str | int | float | bool | None
)
