import logging

from .builder import build_refs_from_registry
from .common import (
    DEFAULT_MAX_DEPTH,
    SOURCE_TYPE,
    DepthLimitExceededError,
    SimpleSpecError,
    Spec,
)
from .typing import TypeChecker, TypeProcessor, TypeResolver
from .walker import DependencyWalker, ReferenceManager


def generate_simple_spec(root_type_obj: SOURCE_TYPE, max_depth: int | None = None) -> Spec:
    """
    Generates a simplified specification (Spec) from a Python type,
    focusing on Pydantic models and dataclasses, resolving nested structures.

    Args:
        root_type_obj: The root Python type (e.g., a Pydantic model, list, dict, dataclass).
        max_depth: Optional maximum nesting depth for referenced models. Defaults to DEFAULT_MAX_DEPTH.

    Returns:
        A Spec object representing the type structure.

    Raises:
        DepthLimitExceededError: If the maximum nesting depth is exceeded.
        SimpleSpecError: For other generation errors.
    """
    # Determine the actual max_depth and create the internal config object
    effective_max_depth = max_depth if max_depth is not None else DEFAULT_MAX_DEPTH
    # Instantiate helper classes
    checker = TypeChecker()
    ref_manager = ReferenceManager(effective_max_depth)
    type_resolver = TypeResolver(ref_manager.resolve_unique_ref_name)
    type_processor = TypeProcessor(checker)
    walker = DependencyWalker(effective_max_depth, ref_manager, type_processor)

    # 1. Walk the type structure to build the reference map
    try:
        root_ref_name = walker.walk(root_type_obj)
    except DepthLimitExceededError as e:
        logging.error(f"Depth limit exceeded during spec generation: {e}")
        raise
    except SimpleSpecError as e:  # Catch our specific errors first
        logging.error(f"SimpleSpec error during dependency walking: {e}", exc_info=True)
        raise  # Re-raise specific SimpleSpec errors
    except (AttributeError, TypeError, ValueError, RecursionError) as e:
        # Catch common errors during type introspection/walking
        logging.error(f"Error during dependency walking: {e}", exc_info=True)
        raise SimpleSpecError(f"Failed to analyze type dependencies: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"Unexpected error during dependency walking: {e}", exc_info=True)
        raise SimpleSpecError(f"Unexpected error analyzing type dependencies: {e}") from e

    # 2. Build Ref objects for all relevant types found
    try:
        all_refs_built, refs_with_depth = build_refs_from_registry(ref_manager, type_resolver, root_ref_name)
    except SimpleSpecError as e:  # Catch specific errors from building if any
        logging.error(f"SimpleSpec error during Ref building: {e}", exc_info=True)
        raise
    except (AttributeError, TypeError, ValueError, KeyError, IndexError) as e:
        # Catch common errors during Ref building phase
        logging.error(f"Error during Ref building: {e}", exc_info=True)
        raise SimpleSpecError(f"Failed during Ref construction: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors during Ref building
        logging.error(f"Unexpected error during Ref building: {e}", exc_info=True)
        raise SimpleSpecError(f"Unexpected error during Ref construction: {e}") from e

    # 3. Get the root Ref object
    root_model_ref = all_refs_built.get(root_ref_name)
    if root_model_ref is None:
        # This should not happen if the walker succeeded, but handle defensively
        raise SimpleSpecError(f"Root model reference '{root_ref_name}' could not be resolved after building Refs.")

    # 4. Sort the dependent refs
    refs_with_depth.sort(key=lambda item: (item[0], item[1].type))  # Sort by depth, then type name
    refs_list = [item[1] for item in refs_with_depth]

    # 5. Construct and return the final Spec
    return Spec(self=root_model_ref, refs=refs_list)
