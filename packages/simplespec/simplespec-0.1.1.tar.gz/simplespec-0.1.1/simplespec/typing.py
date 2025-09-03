import inspect
import logging
from collections.abc import Callable
from dataclasses import is_dataclass
from enum import Enum
from types import NoneType, UnionType
from typing import (
    Any,
    Literal,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from .common import (
    PRIMITIVE_TYPE,
    REFERENCEABLE_TYPE,
    SOURCE_TYPE,
)


def graceful_is_subclass(t1: type, t2: type) -> bool:
    if inspect.isclass(t1) and inspect.isclass(t2):
        try:
            return issubclass(t1, t2)
        except TypeError:
            pass  # Handle cases like issubclass(Any, type)
    return False


class TypeChecker:
    """Unified type checking system."""

    def check(self, t1: Any, type_class: type) -> bool:
        """Base type checking method comparing origin or direct type."""
        origin = get_origin(t1)
        # Check origin or if t1 itself is the type_class (for non-generic types like int, str)
        return origin is type_class or (origin is None and t1 is type_class)

    def is_union(self, t1: Any) -> bool:
        return self.check(t1, Union) or self.check(t1, UnionType)

    def is_dict(self, t1: Any) -> bool:
        return self.check(t1, dict)

    def is_set(self, t1: Any) -> bool:
        return self.check(t1, set)

    def is_tuple(self, t1: Any) -> bool:
        return self.check(t1, tuple)

    def is_list(self, t1: Any) -> bool:
        return self.check(t1, list)

    def is_enum(self, t1: Any) -> bool:
        """Checks if t1 is an Enum class or an instance of one."""
        is_enum_class = inspect.isclass(t1) and graceful_is_subclass(t1, Enum)
        return is_enum_class

    def is_literal(self, t1: Any) -> bool:
        return get_origin(t1) is Literal

    def is_primitive(self, t1: Any) -> bool:
        """Checks if t1 is a primitive type (including NoneType)."""
        # Use isinstance for direct type checks, handles NoneType correctly
        # Check includes uuid.UUID via PRIMITIVE_TYPE definition
        return isinstance(t1, PRIMITIVE_TYPE) or t1 is NoneType or t1 is Any

    def is_referencable(self, t1: Any) -> bool:
        """Checks if t1 is a Pydantic BaseModel OR a dataclass."""
        # Check if it's a class first
        if not inspect.isclass(t1):
            return False
        # Check for BaseModel or dataclass
        return graceful_is_subclass(t1, BaseModel) or is_dataclass(t1)

    def is_complex(self, t1: Any) -> bool:
        """Checks if t1 is a complex type (list, tuple, set, dict, enum, union)."""
        return (
            self.is_list(t1)
            or self.is_tuple(t1)
            or self.is_set(t1)
            or self.is_dict(t1)
            or self.is_enum(t1)
            or self.is_union(t1)
        )


class TypeResolver:
    """Handles resolving Python types to string representations for the Spec."""

    def __init__(self, ref_name_resolver: Callable[[REFERENCEABLE_TYPE], str]):
        """Requires a function to resolve referencable type names (handles collisions)."""
        self._ref_name_resolver = ref_name_resolver
        self._checker = TypeChecker()
        # Dispatch table for complex type resolvers
        self._complex_resolvers = {
            Union: self._resolve_union,
            UnionType: self._resolve_union,
            dict: self._resolve_dict,
            list: self._resolve_list,
            tuple: self._resolve_tuple,
            set: self._resolve_set,
            Enum: self._resolve_enum,  # Handles Enum base
            Literal: self._resolve_literal,  # Handles Literal base
        }

    def _resolve_literal(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        expressions = [f"'{arg}'" if isinstance(arg, str) else repr(arg) for arg in args]  # Use repr for non-str
        return f"Literal[{', '.join(expressions)}]"

    def _resolve_union(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        types = [self.resolve_type_name(arg) for arg in args if arg is not NoneType]
        # Filter out potential duplicates and sort for consistent order
        unique_types = sorted(set(types))
        type_str = " | ".join(unique_types)
        return f"{type_str} | None" if NoneType in args else type_str

    def _resolve_dict(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        if len(args) == 2:  # noqa: PLR2004
            return f"dict[{self.resolve_type_name(args[0])}, {self.resolve_type_name(args[1])}]"
        return "dict"  # Fallback for plain dict

    def _resolve_list(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        if len(args) == 1:
            return f"list[{self.resolve_type_name(args[0])}]"
        return "list"

    def _resolve_tuple(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        if args:
            # Handle variable length tuple Tuple[T, ...]
            if len(args) == 2 and args[1] is Ellipsis:  # noqa: PLR2004
                return f"tuple[{self.resolve_type_name(args[0])}, ...]"
            # Handle fixed length tuple
            types = [self.resolve_type_name(arg) for arg in args]
            return f"tuple[{', '.join(types)}]"
        return "tuple"

    def _resolve_set(self, type_annotation: Any) -> str:
        args = get_args(type_annotation)
        if len(args) == 1:
            return f"set[{self.resolve_type_name(args[0])}]"
        return "set"

    def _resolve_enum(self, type_annotation: Any) -> str:
        if inspect.isclass(type_annotation) and issubclass(type_annotation, Enum):
            # Use repr for values to handle non-strings correctly
            try:
                member_values = [repr(e.value) for e in type_annotation]
                return f"Enum[{', '.join(sorted(member_values))}]"
            except (AttributeError, TypeError, ValueError) as e:  # Handle potential errors during value access/repr
                logging.warning(f"Could not fully resolve Enum members for {type_annotation.__name__}: {e}")
                return type_annotation.__name__  # Fallback to Enum class name
            except Exception as e:  # Catch any other unexpected errors
                logging.error(f"Unexpected error resolving Enum {type_annotation.__name__}: {e}", exc_info=True)
                return f"<ErrorResolvingEnum:{type_annotation.__name__}>"
        return "Enum"  # Generic Enum representation

    def resolve_type_name(self, type_annotation: SOURCE_TYPE) -> str:
        """Resolves a Python type to its string representation."""
        try:
            if type_annotation is Any:
                return "Any"
            if type_annotation is NoneType:
                return "None"

            origin = get_origin(type_annotation)
            resolver = self._complex_resolvers.get(origin)

            if resolver:
                return resolver(type_annotation)
            elif self._checker.is_enum(type_annotation):  # Handle direct Enum classes not caught by origin
                return self._resolve_enum(type_annotation)
            elif self._checker.is_referencable(type_annotation):
                return self._ref_name_resolver(type_annotation)
            elif self._checker.is_primitive(type_annotation) or inspect.isclass(type_annotation):
                return type_annotation.__name__
            else:
                # Fallback for unknown types (like TypeVars, etc.)
                # Attempt to resolve ForwardRefs if possible
                # Note: Proper ForwardRef resolution requires context (globals/locals)
                # which is complex to handle robustly here. Pydantic's model_rebuild helps.
                type_str = str(type_annotation)
                # Basic check for ForwardRef pattern
                if type_str.startswith("ForwardRef("):
                    return type_str[len("ForwardRef('") : -2]  # Extract the name
                return type_str

        except (AttributeError, TypeError, ValueError, IndexError) as e:
            logging.warning(f"Known error resolving type '{type_annotation}': {e}")
            # Fallback to string representation if possible, otherwise indicate error
            try:
                return str(type_annotation)
            except Exception:
                return f"<UnrepresentableType:{type(type_annotation).__name__}>"
        except Exception as e:
            logging.error(f"Unexpected error resolving type '{type_annotation}': {e}", exc_info=True)
            return f"<ErrorResolving:{type_annotation}>"


class TypeProcessor:
    """Knows how to extract child types from complex Python types for dependency analysis."""

    def __init__(self, checker: TypeChecker):
        self._checker = checker
        # Map checker function to processor method
        self._processor_map = {
            self._checker.is_referencable: self._process_referencable_type,
            self._checker.is_union: self._process_union,
            self._checker.is_dict: self._process_dict,
            self._checker.is_list: self._process_list_or_set,
            self._checker.is_set: self._process_list_or_set,
            self._checker.is_tuple: self._process_tuple,
        }

    def get_child_types(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        """Return a list of child types that need to be processed for the given type."""
        # Attempt to rebuild Pydantic model to resolve forward refs before processing fields
        if inspect.isclass(current_type) and graceful_is_subclass(current_type, BaseModel):
            try:
                current_type.model_rebuild(force=True)
            except Exception as e:
                logging.warning(f"Failed to rebuild model {current_type.__name__} during child type extraction: {e}")

        for checker_func, processor_method in self._processor_map.items():
            # Special handling for is_referencable as it now covers two types
            if checker_func == self._checker.is_referencable and checker_func(current_type):
                return self._process_referencable_type(current_type)
            elif checker_func != self._checker.is_referencable and checker_func(current_type):
                return processor_method(current_type)
        return []  # Primitives, Enums, Literals have no children to process here

    def _process_referencable_type(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        """Extract child types for Pydantic models or dataclasses."""
        from dataclasses import fields as dataclass_fields  # Local import

        if not inspect.isclass(current_type):
            return []

        if graceful_is_subclass(current_type, BaseModel):
            try:
                return [field_info.annotation for field_info in current_type.model_fields.values()]
            except AttributeError:
                logging.warning(
                    f"Could not access model_fields for Pydantic model {current_type.__name__}. Returning no children."
                )
                return []
            except Exception as e:  # Keep broader catch here as model_fields access can be complex
                logging.error(f"Error processing Pydantic model fields for {current_type.__name__}: {e}")
                return []
        elif is_dataclass(current_type):
            try:
                # For dataclasses, we need to handle potential ForwardRefs more carefully
                # typing.get_type_hints might be needed for complex cases, but let's start simple
                return [f.type for f in dataclass_fields(current_type)]
            except (TypeError, AttributeError, NameError) as e:  # Errors during field access or type resolution
                logging.error(f"Error processing dataclass fields for {current_type.__name__}: {e}")
                return []
            except Exception as e:  # Catch other unexpected errors
                logging.error(f"Unexpected error processing dataclass fields for {current_type.__name__}: {e}")
                return []
        else:
            # Should not be reached if called correctly via the map
            return []

    def _process_union(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        return [arg for arg in get_args(current_type) if arg is not NoneType]

    def _process_dict(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        args = get_args(current_type)
        return list(args) if len(args) == 2 else []  # noqa: PLR2004

    def _process_list_or_set(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        args = get_args(current_type)
        return list(args) if len(args) == 1 else []

    def _process_tuple(self, current_type: SOURCE_TYPE) -> list[SOURCE_TYPE]:
        args = get_args(current_type)
        if args and args[-1] is Ellipsis:
            return [args[0]] if len(args) == 2 else []  # noqa: PLR2004
        return list(args)
