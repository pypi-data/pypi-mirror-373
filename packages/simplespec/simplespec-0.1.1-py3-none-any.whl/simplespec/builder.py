import inspect
import logging
from dataclasses import MISSING, is_dataclass
from dataclasses import fields as dataclass_fields
from typing import Any

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MinLen, MultipleOf
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic_core import PydanticUndefinedType

from .common import Prop, Ref
from .typing import TypeResolver, graceful_is_subclass
from .walker import ReferenceManager


def _extract_pydantic_constraints(field_info: PydanticField) -> dict[str, Any]:
    """Extract constraints from Pydantic field metadata using snake_case keys."""
    constraints = {}

    # Default value
    default = field_info.get_default()
    if default is not None and not isinstance(default, PydanticUndefinedType):
        constraints["default"] = default  # Store raw default

    # Metadata constraints - map type to attribute name (which is snake_case)
    attr_map = {
        Gt: "gt",
        Ge: "ge",
        Lt: "lt",
        Le: "le",
        MinLen: "min_length",
        MaxLen: "max_length",
        MultipleOf: "multiple_of",
    }

    if field_info.metadata:
        for constraint_obj in field_info.metadata:
            constraint_type = type(constraint_obj)
            if constraint_type in attr_map:
                key_name = attr_map[constraint_type]
                # Use getattr to fetch the constraint value using its snake_case name
                constraints[key_name] = getattr(constraint_obj, key_name)

    return constraints


def _extract_dataclass_constraints(field_info) -> dict[str, Any]:  # field_info is a dataclasses.Field
    """Extracts default constraints from a dataclass field."""
    constraints = {}
    if field_info.default is not MISSING:
        constraints["default"] = field_info.default
    elif field_info.default_factory is not MISSING:
        # Representing default_factory is tricky, maybe just note its presence?
        # constraints["default_factory"] = True # Or similar
        pass  # Currently skipping default_factory representation
    return constraints


def _format_prop_description(base_description: str | None, constraints: dict[str, Any]) -> str | None:
    """Combines base description with formatted constraints."""
    constraints_str = ""
    if constraints:
        # Use snake_case keys and repr for values
        constraints_str = " " + " ".join(f"[{k}={v!r}]" for k, v in sorted(constraints.items()))
    full_description = (base_description or "").strip() + constraints_str
    return full_description.strip() or None


def _get_model_description(model_type: type) -> str | None:
    """Extract description from docstring or Pydantic title for a model/dataclass.

    Uses the direct __doc__ attribute to avoid inheriting parent docstrings (e.g., from BaseModel).
    """
    if not (inspect.isclass(model_type) and (graceful_is_subclass(model_type, BaseModel) or is_dataclass(model_type))):
        return None

    # Use model_type.__doc__ directly to avoid inheritance via inspect.getdoc
    direct_doc = getattr(model_type, "__doc__", None)
    doc = inspect.cleandoc(direct_doc) if isinstance(direct_doc, str) else None

    # Pydantic v2 uses model_config['title'] - prefer direct docstring if available
    title = None
    if graceful_is_subclass(model_type, BaseModel):
        # Ensure model_config exists and is a dict before accessing
        model_config = getattr(model_type, "model_config", None)
        if isinstance(model_config, dict):
            title = model_config.get("title")

    desc = doc or title  # Prefer docstring, fallback to title
    return desc.replace("\n", " ").strip() if desc else None


def _build_model_properties(model_type: type[BaseModel], type_resolver: TypeResolver) -> dict[str, Prop]:
    """Builds the dictionary of Prop objects for a Pydantic model's fields."""
    properties: dict[str, Prop] = {}
    try:
        # Ensure model is up-to-date (for forward refs)
        model_type.model_rebuild(force=True)
        model_fields = model_type.model_fields
    except (AttributeError, TypeError, RuntimeError) as model_error:
        # Catch common errors during model processing (e.g., rebuild failure)
        resolved_type_name = type_resolver.resolve_type_name(model_type)
        logging.error(f"Could not process fields for model {resolved_type_name}: {model_error}")
        return {}  # Return empty properties if fields cannot be accessed

    for field_name, field_info in model_fields.items():
        field_type = field_info.annotation
        prop_type_str = type_resolver.resolve_type_name(field_type)
        constraints = _extract_pydantic_constraints(field_info)
        prop_description = _format_prop_description(field_info.description, constraints)

        prop = Prop(type=prop_type_str, description=prop_description)
        properties[field_name] = prop
    return properties


def _build_dataclass_properties(dataclass_type: type, type_resolver: TypeResolver) -> dict[str, Prop]:
    """Builds the dictionary of Prop objects for a dataclass's fields."""
    properties: dict[str, Prop] = {}
    try:
        # Consider using get_type_hints here for better forward ref resolution if needed
        # hints = typing.get_type_hints(dataclass_type)
        dc_fields = dataclass_fields(dataclass_type)
    except (TypeError, AttributeError, NameError) as e:
        # Catch specific errors expected during field introspection
        logging.error(f"Could not get fields for dataclass {dataclass_type.__name__}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error getting fields for dataclass {dataclass_type.__name__}: {e}", exc_info=True)
        return {}

    for field_info in dc_fields:
        field_name = field_info.name
        field_type = field_info.type  # Might need hints[field_name] for complex cases

        prop_type_str = type_resolver.resolve_type_name(field_type)

        # Extract default value constraints
        constraints = _extract_dataclass_constraints(field_info)

        # Dataclasses don't have standard field descriptions, use constraints only
        prop_description = _format_prop_description(None, constraints)

        prop = Prop(type=prop_type_str, description=prop_description)
        properties[field_name] = prop
    return properties


def build_refs_from_registry(
    ref_manager: ReferenceManager, type_resolver: TypeResolver, root_ref_name: str
) -> tuple[dict[str, Ref], list[tuple[int, Ref]]]:
    """Builds Ref objects for all relevant types found during the walk."""
    all_refs_built: dict[str, Ref] = {}
    refs_with_depth: list[tuple[int, Ref]] = []

    for info in ref_manager.get_all_ref_info():
        raw_type = info.raw_type
        is_referencable = info.is_referencable

        # Decide if we need to create a full Ref for this type
        # We always need one for the root, and for any referencable models/dataclasses.
        if not (is_referencable or info.ref_name == root_ref_name):
            continue

        try:
            resolved_type_name = type_resolver.resolve_type_name(raw_type)
            description = _get_model_description(raw_type)
            properties: dict[str, Prop] = {}

            if is_referencable and inspect.isclass(raw_type):
                if graceful_is_subclass(raw_type, BaseModel):
                    properties = _build_model_properties(raw_type, type_resolver)
                elif is_dataclass(raw_type):
                    properties = _build_dataclass_properties(raw_type, type_resolver)

            # Create the Ref object
            ref_obj = Ref(type=resolved_type_name, description=description, properties=properties)
            all_refs_built[info.ref_name] = ref_obj

            # Add referencable models (excluding the root if it's also referencable)
            # to the list for sorting refs later.
            if is_referencable and info.ref_name != root_ref_name:
                refs_with_depth.append((info.depth, ref_obj))

        except (AttributeError, TypeError, ValueError, KeyError, IndexError) as build_error:
            # Catch common errors during Ref building (introspection, dict access)
            logging.error(f"Failed to build Ref for {info.ref_name} ({raw_type}): {build_error}", exc_info=True)
            # Optionally create a placeholder Ref or skip
            placeholder_ref = Ref(type=f"<Error:{info.ref_name}>", description=f"Failed to build: {build_error}")
            all_refs_built[info.ref_name] = placeholder_ref
            if is_referencable and info.ref_name != root_ref_name:
                refs_with_depth.append((info.depth, placeholder_ref))
        except Exception as unexpected_error:  # Catch any other unexpected errors
            logging.critical(
                f"Unexpected critical error building Ref for {info.ref_name} ({raw_type}): {unexpected_error}",
                exc_info=True,
            )
            placeholder_ref = Ref(
                type=f"<CriticalError:{info.ref_name}>", description=f"Unexpected build error: {unexpected_error}"
            )
            all_refs_built[info.ref_name] = placeholder_ref
            if is_referencable and info.ref_name != root_ref_name:
                refs_with_depth.append((info.depth, placeholder_ref))

    return all_refs_built, refs_with_depth
