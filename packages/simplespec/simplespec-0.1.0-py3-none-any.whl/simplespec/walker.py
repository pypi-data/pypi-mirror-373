import inspect
import logging
from types import NoneType

from .common import (
    NON_REFERENCEABLE_PREFIX,
    REFERENCEABLE_PREFIX,
    REFERENCEABLE_TYPE,
    SOURCE_TYPE,
    DepthLimitExceededError,
    RefInfo,
    TypeNotFoundError,
)
from .typing import TypeChecker, TypeProcessor


class ReferenceManager:
    """Handles reference tracking and naming consolidation."""

    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self._ref_info: dict[str, RefInfo] = {}  # ref_name -> RefInfo
        self._type_to_ref_name: dict[SOURCE_TYPE, str] = {}  # type -> ref_name (for quick lookup)
        self._name_map: dict[str, dict[str, bool]] = {}  # class_name -> {ref_name: True} (for collision detection)
        self._checker = TypeChecker()  # Use the checker

    def _generate_ref_name(self, _type: SOURCE_TYPE) -> str:
        """Generate a reference name based on type."""
        # Use the same prefix logic for both Pydantic models and dataclasses
        prefix = REFERENCEABLE_PREFIX if self._checker.is_referencable(_type) else NON_REFERENCEABLE_PREFIX
        # Use a stable representation, e.g., qualified name if available
        type_str = getattr(_type, "__qualname__", str(_type))
        # Simple sanitize: replace brackets/commas often found in generic type strings
        safe_type_str = type_str.replace("[", "_").replace("]", "").replace(", ", "_")
        return f"{prefix}{safe_type_str}"

    def register_type(self, _type: SOURCE_TYPE, depth: int) -> str:
        """Register a type if not already present and return its reference name."""
        if _type in self._type_to_ref_name:
            # Type already seen, return existing name
            return self._type_to_ref_name[_type]

        base_ref_name = self._generate_ref_name(_type)
        ref_name = base_ref_name

        # Handle potential collisions
        counter = 0
        while ref_name in self._ref_info:
            counter += 1
            ref_name = f"{base_ref_name}_{counter}"

        # Store info
        is_ref = self._checker.is_referencable(_type)
        info = RefInfo(ref_name=ref_name, raw_type=_type, depth=depth, is_referencable=is_ref)
        self._ref_info[ref_name] = info
        self._type_to_ref_name[_type] = ref_name

        # Update name map if it's a referencable class (for collision resolution)
        if is_ref and inspect.isclass(_type):
            class_name = _type.__name__
            if class_name not in self._name_map:
                self._name_map[class_name] = {}
            self._name_map[class_name][ref_name] = True

        return ref_name

    def get_ref_info(self, ref_name: str) -> RefInfo | None:
        """Get RefInfo by reference name."""
        return self._ref_info.get(ref_name)

    def get_type(self, ref_name: str) -> SOURCE_TYPE:
        """Get raw type by reference name."""
        info = self.get_ref_info(ref_name)
        if info is None:
            raise TypeNotFoundError(f"Type reference '{ref_name}' not found")
        return info.raw_type

    def get_depth(self, ref_name: str) -> int:
        """Get depth by reference name."""
        info = self.get_ref_info(ref_name)
        if info is None:
            raise TypeNotFoundError(f"Type reference '{ref_name}' not found")
        return info.depth

    def get_ref_name(self, _type: SOURCE_TYPE) -> str | None:
        """Get the reference name for a given type."""
        return self._type_to_ref_name.get(_type)

    def get_all_ref_info(self) -> list[RefInfo]:
        """Return all stored RefInfo objects."""
        return list(self._ref_info.values())

    def resolve_unique_ref_name(self, _type: REFERENCEABLE_TYPE) -> str:
        """Resolve a potentially ambiguous reference name to a unique one based on depth."""
        if not inspect.isclass(_type):
            # This case should ideally not be hit if called correctly, but protects
            # return str(_type)
            # Let's use the existing logic to get the potentially non-unique name first
            current_ref_name = self.get_ref_name(_type)
            if current_ref_name:
                # Find the info to get the class name from the type
                info = self.get_ref_info(current_ref_name)
                if info and inspect.isclass(info.raw_type):
                    return info.raw_type.__name__  # Fallback to class name
            # Last resort fallback
            logging.warning(f"Could not resolve unique name for non-class type: {_type}")
            return str(_type)

        class_name = _type.__name__
        possible_refs_dict = self._name_map.get(class_name, {})

        # If no collision or only one entry for this class name, use the simple class name
        if len(possible_refs_dict) <= 1:
            return class_name

        # Attempt to find the specific registered ref_name for this exact type object
        current_ref_name = self.get_ref_name(_type)
        if current_ref_name is None:
            logging.warning(f"Could not find registered ref_name for {_type}. Using class name.")
            return class_name  # Fallback if registration somehow failed before resolution

        # If there are multiple refs with the same base class name, resolve using depth
        refs_with_depth = []
        for ref_name_candidate in possible_refs_dict:
            info_candidate = self.get_ref_info(ref_name_candidate)
            if info_candidate:
                refs_with_depth.append((ref_name_candidate, info_candidate.depth))
            else:
                logging.warning(f"Missing info for conflicting ref '{ref_name_candidate}'. Assigning max depth.")
                refs_with_depth.append((ref_name_candidate, float("inf")))

        # Sort refs based on depth (ascending), then by ref_name for stability
        refs_with_depth.sort(key=lambda item: (item[1], item[0]))

        # Map the sorted ref_names to their base class name + suffix if needed
        sorted_ref_names = [item[0] for item in refs_with_depth]

        try:
            index = sorted_ref_names.index(current_ref_name)
            # The first one (lowest depth) gets the base name, subsequent ones get suffix
            return class_name if index == 0 else f"{class_name}_{index}"
        except ValueError:
            # Should not happen if current_ref_name was found in possible_refs_dict
            logging.warning(
                f"current_ref_name {current_ref_name} not found in depth-sorted list for {class_name}. Using class name."
            )
            return class_name
        except (AttributeError, TypeError, KeyError, IndexError) as e:
            # Catch potential errors during info access or list operations
            logging.warning(f"Error resolving unique name for {class_name}: {e}. Using class name.")
            return class_name
        except Exception as e:
            logging.error(f"Unexpected error resolving unique name for {class_name}: {e}", exc_info=True)
            return class_name  # Fallback


class DependencyWalker:
    """Handles walking the type structure to build the dependency graph."""

    def __init__(self, max_depth: int, ref_manager: ReferenceManager, type_processor: TypeProcessor):
        self.max_depth = max_depth
        self._ref_manager = ref_manager
        self._type_processor = type_processor
        self._processed_types: set[SOURCE_TYPE] = set()

    def walk(self, root_type: SOURCE_TYPE) -> str:
        """Start the dependency walk from the root type."""
        return self._build_dependency_tree(0, root_type)

    def _build_dependency_tree(self, depth: int, current_type: SOURCE_TYPE) -> str:
        """Recursively build the reference map using dispatch handlers."""
        # Handle cycles/already processed types
        existing_ref_name = self._ref_manager.get_ref_name(current_type)
        if existing_ref_name:
            # If already fully processed or currently being processed at shallower depth
            # No need to re-process or go deeper
            return existing_ref_name

        # Avoid processing built-in types like NoneType directly in the recursion if they slip through
        if current_type is NoneType:
            # We handle NoneType within Unions/Optionals, no need to process standalone
            return "None"  # Or some indicator? Let TypeResolver handle final string.

        if depth > self.max_depth:
            raise DepthLimitExceededError(f"Max depth {self.max_depth} exceeded processing type: {current_type}")

        # Register the type BEFORE processing children to handle recursion
        ref_name = self._ref_manager.register_type(current_type, depth)

        # Mark as currently being processed (using presence in _type_to_ref_name map)
        # No, registration handles this. We need _processed_types for post-registration checks?
        # Let's simplify: registration itself marks it as seen.

        # Get child types from the processor and walk them
        child_types = self._type_processor.get_child_types(current_type)
        for child_type in child_types:
            self._build_dependency_tree(depth + 1, child_type)

        return ref_name
