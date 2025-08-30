from dataclasses import fields, is_dataclass
import dataclasses
from typing import Any, Dict, List, Literal, Type, get_args, get_origin, get_type_hints


def extract_prop_metadata(cls: Type, field: dataclasses.Field) -> Dict[str, Any]:
    """
    Inspects a dataclass field and extracts metadata for UI rendering.

    This function infers the appropriate frontend component (e.g., slider, checkbox)
    based on the field's type hint if not explicitly specified in the metadata.
    
    Args:
        cls: The dataclass instance containing the field.
        field: The dataclasses.Field object to inspect.
    Returns:
        A dictionary of metadata for the frontend to render a property control.
    """
    metadata = field.metadata.copy()
    metadata["name"] = field.name
    current_value = getattr(cls, field.name)
    metadata["value"] = current_value if current_value is not None else (
        field.default if field.default is not dataclasses.MISSING else None
    )
    metadata["label"] = metadata.get("label", field.name.replace("_", " ").capitalize())
    
    prop_type = get_type_hints(type(cls)).get(field.name)
    
    # Set default component based on type if not specified
    if "component" not in metadata:
        if prop_type is bool:
            metadata["component"] = "checkbox"
        elif prop_type is int:
            metadata["component"] = "number_integer"
        elif prop_type is float:
            metadata["component"] = "number_float"
        elif get_origin(prop_type) is Literal:
            metadata["component"] = "dropdown"
        else:
            metadata["component"] = "string"
    
    # Handle choices for dropdown and radio components with Literal types
    if metadata.get("component") in ["dropdown", "radio"] and get_origin(prop_type) is Literal:
        choices = list(get_args(prop_type))
        metadata["choices"] = choices
        if metadata["value"] not in choices:
            metadata["value"] = choices[0] if choices else None
    
    return metadata


def build_path_to_metadata_key_map(cls: Type, prefix_list: List[str]) -> Dict[str, str]:
    """
    Builds a map from a dataclass field path (e.g., 'image_settings.model') to the
    expected key in the metadata dictionary (e.g., 'Image Settings - Model').
    """
    path_map = {}
    if not is_dataclass(cls):
        return {}

    for f in fields(cls):
        current_path = f.name
        
        if is_dataclass(f.type):
            parent_label = f.metadata.get("label", f.name.replace("_", " ").title())
            new_prefix_list = prefix_list + [parent_label]
            nested_map = build_path_to_metadata_key_map(f.type, new_prefix_list)
            for nested_path, metadata_key in nested_map.items():
                path_map[f"{current_path}.{nested_path}"] = metadata_key
        else:
            label = f.metadata.get("label", f.name.replace("_", " ").title())
            full_prefix = " - ".join(prefix_list)
            metadata_key = f"{full_prefix} - {label}" if full_prefix else label
            path_map[current_path] = metadata_key
            
    return path_map


def build_dataclass_fields(cls: Type, prefix: str = "") -> Dict[str, str]:
    """
    Recursively builds a mapping of field labels to field paths for a dataclass.

    This function traverses a dataclass and its nested dataclasses, creating a dictionary
    that maps metadata labels (from `metadata={"label": ...}`) to dot-separated field paths
    (e.g., "image_settings.model"). It is used to associate metadata labels with their
    corresponding fields in a dataclass hierarchy.

    Args:
        cls: The dataclass type to process (e.g., PropertyConfig).
        prefix: A string prefix for field paths, used during recursion to track nested fields.

    Returns:
        A dictionary mapping metadata labels (str) to field paths (str).
        Example: `{"Model": "image_settings.model", "Description": "description"}`
    """
    dataclass_fields = {}
    type_hints = get_type_hints(cls)
    
    for field in fields(cls):
        field_name = field.name
        field_type = type_hints.get(field_name, field.type)
        field_label = field.metadata.get('label')
        current_path = f"{prefix}{field_name}" if prefix else field_name

        if field_label:
            dataclass_fields[field_label] = current_path
        if is_dataclass(field_type):
            sub_fields = build_dataclass_fields(field_type, f"{current_path}.")
            dataclass_fields.update(sub_fields)
    
    return dataclass_fields


def create_dataclass_instance(cls: Type, data: Dict[str, Any]) -> Any:
    """
    Recursively creates an instance of a dataclass from a nested dictionary.

    This function constructs an instance of the specified dataclass, populating its fields
    with values from the provided dictionary. For fields that are themselves dataclasses,
    it recursively creates instances of those dataclasses. If a field is missing from the
    dictionary, it uses the field's default value or default_factory.

    Args:
        cls: The dataclass type to instantiate (e.g., PropertyConfig).
        data: A dictionary containing field values, which may be nested to match the dataclass hierarchy.

    Returns:
        An instance of the dataclass with fields populated from the dictionary.
    """
    kwargs = {}
    type_hints = get_type_hints(cls)
    
    for field in fields(cls):
        field_name = field.name
        field_type = type_hints.get(field_name, field.type)
        if field_name in data:
            if is_dataclass(field_type) and isinstance(data[field_name], dict):
                kwargs[field_name] = create_dataclass_instance(field_type, data[field_name])
            else:
                kwargs[field_name] = field.default if data[field_name] is None else data[field_name]
        else:
            if field.default_factory is not None:
                kwargs[field_name] = field.default_factory()
            else:
                kwargs[field_name] = field.default
    
    return cls(**kwargs)


def flatten_dataclass_with_labels(instance: Any, prefix_labels: List[str] = []) -> Dict[str, Any]:
    """
    Recursively flattens a dataclass instance, creating a dictionary
    where the key is a hierarchical, dash-separated label string.
    """
    flat_map = {}
    if not is_dataclass(instance):
        return {}

    for f in fields(instance):
        value = getattr(instance, f.name)
        
        if is_dataclass(value):
            group_label = f.metadata.get("label", f.name.replace("_", " ").title())
            new_prefix_list = prefix_labels + [group_label]
            flat_map.update(flatten_dataclass_with_labels(value, new_prefix_list))
        else:
            field_label = f.metadata.get("label", f.name.replace("_", " ").title())
            all_labels = prefix_labels + [field_label]
            hierarchical_key = " - ".join(all_labels)
            flat_map[hierarchical_key] = value
            
    return flat_map