"""Type aliases used throughout dotevals."""

from typing import TypeAlias

# Type aliases for score values and data structures
Primitive: TypeAlias = bool | int | float | str | None
JSONValue: TypeAlias = Primitive | dict[str, "JSONValue"] | list["JSONValue"]
ScoreValue: TypeAlias = (
    bool | int | float | str | dict[str, Primitive] | list[Primitive]
)
DatasetRow: TypeAlias = dict[str, JSONValue]
Metadata: TypeAlias = dict[str, Primitive]
