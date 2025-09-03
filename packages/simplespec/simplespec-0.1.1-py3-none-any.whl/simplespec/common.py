import uuid
from dataclasses import dataclass, field
from enum import Enum
from types import UnionType

from pydantic import BaseModel

# Type definitions
PRIMITIVE_TYPE = int | float | str | bool | bytes | bytearray | uuid.UUID
COMPLEX_TYPE = list | tuple | set | Enum | dict | UnionType
REFERENCEABLE_TYPE = BaseModel  # Will add dataclasses later dynamically
SOURCE_TYPE = PRIMITIVE_TYPE | COMPLEX_TYPE | REFERENCEABLE_TYPE | type

DEFAULT_MAX_DEPTH = 4

# Constants (Replaced ReferenceTypes class)
REFERENCEABLE_PREFIX = "R__"
NON_REFERENCEABLE_PREFIX = "NR__"


# Custom Exceptions
class SimpleSpecError(Exception):
    """Base exception for SimpleSpec errors."""

    pass


class DepthLimitExceededError(SimpleSpecError):
    """Raised when the maximum depth limit is exceeded."""

    pass


class TypeNotFoundError(SimpleSpecError):
    """Raised when a type cannot be found in references."""

    pass


# --- Output Data Structures ---
@dataclass
class Prop:
    type: str
    description: str | None = None

    def __str__(self) -> str:
        representation_str = f"{self.type}"
        if self.description:
            representation_str += f", {self.description}"
        return representation_str


@dataclass
class Ref:
    type: str
    description: str | None = None
    properties: dict[str, Prop] = field(default_factory=dict)

    def __str__(self) -> str:
        description_str = f", {self.description}" if self.description else ""
        representation_str = f"{self.type}{description_str}"
        for key, prop in self.properties.items():
            representation_str += f"\n    {key}: {prop}"
        return representation_str


@dataclass
class Spec:
    self: Ref
    refs: list[Ref] = field(default_factory=list)

    def __str__(self) -> str:
        if len(self.refs) > 0:
            str_refs = "Referenced specs:\n" + "\n".join([str(ref) for ref in self.refs])
            str_spec = f"Spec:\n{self.self!s}"
            return str_refs + "\n" + str_spec
        return str(self.self)


# Internal tracking structure
@dataclass
class RefInfo:
    """Stores metadata about a referenced type."""

    ref_name: str
    raw_type: SOURCE_TYPE
    depth: int
    is_referencable: bool  # Is it a BaseModel/dataclass needing its own entry in Spec.refs?
