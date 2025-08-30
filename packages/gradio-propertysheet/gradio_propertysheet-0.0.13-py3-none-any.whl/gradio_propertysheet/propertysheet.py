from __future__ import annotations
import copy
import json
from typing import Any, Dict, List, get_type_hints
import dataclasses
from gradio.components.base import Component
from gradio_propertysheet.helpers import extract_prop_metadata
from gradio_client.documentation import document
from gradio.events import Events, EventListener

def prop_meta(**kwargs) -> dataclasses.Field:
    """
    A helper function to create a dataclass field with Gradio-specific metadata.
    
    Returns:
        A dataclasses.Field instance with the provided metadata.
    """
    return dataclasses.field(metadata=kwargs)

@document()
class PropertySheet(Component):
    """
    A Gradio component that renders a dynamic UI from a Python dataclass instance.
    It allows for nested settings and automatically infers input types.
    """
    undo = EventListener(
        "undo",
        doc="This listener is triggered when the user clicks the undo button in component.",        
    )

    EVENTS = [        
        Events.change,
        Events.input,
        Events.expand,
        Events.collapse,
        undo        
    ]
    
    def __init__(
        self, 
        value: Any | None = None, 
        *,  
        label: str | None = None,
        root_label: str = "General",
        show_group_name_only_one: bool = True,
        root_properties_first: bool = True,
        disable_accordion: bool = False,
        visible: bool = True,
        open: bool = True,
        elem_id: str | None = None,
        scale: int | None = None,
        width: int | str | None = None,
        height: int | str | None = None,
        min_width: int | None = None,
        container: bool = True,
        elem_classes: list[str] | str | None = None,
        **kwargs
    ):
        """
        Initializes the PropertySheet component.

        Args:
            value: The initial dataclass instance to render.
            label: The main label for the component, displayed in the accordion header.
            root_label: The label for the root group of properties.
            show_group_name_only_one: If True, only the group name is shown when there is a single group.
            root_properties_first: If True (default), root-level properties are rendered before nested groups. If False, they are rendered after.
            disable_accordion: If True, disables the accordion functionality.
            visible: If False, the component will be hidden.
            open: If False, the accordion will be collapsed by default.
            elem_id: An optional string that is assigned as the id of this component in the DOM.
            scale: The relative size of the component in its container.
            width: The width of the component in pixels.
            height: The maximum height of the component's content area in pixels before scrolling.
            min_width: The minimum width of the component in pixels.
            container: If True, wraps the component in a container with a background.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the DOM.
        """
        if value is not None and not dataclasses.is_dataclass(value):
            raise ValueError("Initial value must be a dataclass instance")
        
        # Store the current dataclass instance and its type.
        # These might be None if the component is initialized without a value.
        self._dataclass_value = copy.deepcopy(value) if value is not None else None
        self._dataclass_type = type(value) if dataclasses.is_dataclass(value) else None
        
        self.width = width
        self.height = height
        self.open = open
        self.root_label = root_label
        self.show_group_name_only_one = show_group_name_only_one
        self.root_properties_first = root_properties_first
        self.disable_accordion = disable_accordion
        
        super().__init__(
            label=label, visible=visible, elem_id=elem_id, scale=scale,
            min_width=min_width, container=container, elem_classes=elem_classes,
            value=self._dataclass_value, **kwargs
        )

    
    @document()
    def postprocess(self, value: Any) -> List[Dict[str, Any]]:
        """
        Converts the Python dataclass instance into a JSON schema for the frontend.

        Crucially, this method also acts as a "state guardian". When Gradio calls it
        with a valid dataclass (e.g., during a `gr.update` that makes the component visible),
        it synchronizes the component's internal state (`_dataclass_value` and `_dataclass_type`),
        ensuring the object is "rehydrated" and ready for `preprocess`.
        
        Args:
            value: The dataclass instance to process.
        Returns:
            A list representing the JSON schema for the frontend UI.
        """
        if dataclasses.is_dataclass(value):
            self._dataclass_value = copy.deepcopy(value)
            # Restore the dataclass type if it was lost (e.g., on re-initialization).
            if self._dataclass_type is None:
                self._dataclass_type = type(value)
        
        current_value = self._dataclass_value

        if current_value is None or not dataclasses.is_dataclass(current_value): 
            return []
            
        json_schema, root_properties = [], []      
        used_group_names = set()

        # Process nested dataclasses first
        for field in dataclasses.fields(current_value):      
            field_type = get_type_hints(type(current_value)).get(field.name)
            is_nested_dataclass = dataclasses.is_dataclass(field_type) if isinstance(field_type, type) else False

            if is_nested_dataclass:
                group_obj = getattr(current_value, field.name)
                group_props = []
                group_type = type(group_obj)
                parent_dataclass = next((b for b in group_type.__bases__ if dataclasses.is_dataclass(b)), None)
                
                reordered_fields = []
                if parent_dataclass:                    
                    all_fields = dataclasses.fields(group_type)
                    parent_field_names = {f.name for f in dataclasses.fields(parent_dataclass)}
                                        
                    own_fields = [f for f in all_fields if f.name not in parent_field_names]                    
                    inherited_fields = [f for f in all_fields if f.name in parent_field_names]                                        
                    reordered_fields = own_fields + inherited_fields
                else:                    
                    reordered_fields = dataclasses.fields(group_type)
                                
                for group_field in reordered_fields:
                    metadata = extract_prop_metadata(group_obj, group_field)                
                    if "interactive_if" in metadata and "." not in metadata["interactive_if"]["field"]:
                        relative_field_name = metadata["interactive_if"]["field"]
                        metadata["interactive_if"]["field"] = f"{field.name}.{relative_field_name}"
                    
                    metadata["name"] = f"{field.name}.{group_field.name}"
                    group_props.append(metadata)
                                
                base_group_name = field.metadata.get("label", field.name.replace("_", " ").title())
                unique_group_name = base_group_name
                counter = 2
                while unique_group_name in used_group_names:
                    unique_group_name = f"{base_group_name} ({counter})"
                    counter += 1
                
                used_group_names.add(unique_group_name)
                json_schema.append({"group_name": unique_group_name, "properties": group_props})
            else:
                root_properties.append(extract_prop_metadata(current_value, field))
        
        # Process root properties, if any exist
        if root_properties:           
            base_root_label = self.root_label
            unique_root_label = base_root_label
            counter = 2
            # Apply the same logic to the root label
            while unique_root_label in used_group_names:
                unique_root_label = f"{base_root_label} ({counter})"
                counter += 1
            
            root_group = {"group_name": unique_root_label, "properties": root_properties}            
            if self.root_properties_first:
                json_schema.insert(0, root_group)
            else:
                json_schema.append(root_group)            
        
        return json_schema
    
    @document()
    def preprocess(self, payload: Any) -> Any:
        """
        Processes the payload from the frontend to create an updated dataclass instance.

        This method is stateless regarding the instance value. It reconstructs the object
        from scratch using the `_dataclass_type` (which is reliably set by `postprocess`)
        and then applies the changes from the payload.
        
        Args:
            payload: The data received from the frontend, typically a list of property groups.
        Returns:
            A new, updated instance of the dataclass.
        """        
        if self._dataclass_type is None or payload is None:
            return None

        reconstructed_obj = self._dataclass_type()
        value_map = {}

        if isinstance(payload, list):
            for group in payload:
                group_name_key = None
                # Handle the root group
                potential_root_name = group["group_name"].replace(" (Root)", "")
                if potential_root_name == self.root_label:
                    group_name_key = None
                else:
                    # Check dataclass fields for a matching name or metadata label
                    for f in dataclasses.fields(reconstructed_obj):
                        # Check metadata label first
                        metadata_label = f.metadata.get("label", f.name.replace("_", " ").title())
                        if metadata_label == group["group_name"]:
                            group_name_key = f.name
                            break
                        # Fallback to field name
                        if f.name.replace("_", " ").title() == group["group_name"]:
                            group_name_key = f.name
                            break

                for prop in group.get("properties", []):
                    full_key = prop["name"]
                    if '.' not in full_key and group_name_key is not None:
                        full_key = f"{group_name_key}.{prop['name']}"
                    
                    value_map[full_key] = prop["value"]
        
        elif isinstance(payload, dict):
            value_map = payload

        # Populate the fresh object using the flattened value_map
        for field in dataclasses.fields(reconstructed_obj):
            if dataclasses.is_dataclass(field.type):
                group_obj = getattr(reconstructed_obj, field.name)
                for group_field in dataclasses.fields(group_obj):
                    nested_key = f"{field.name}.{group_field.name}"
                    if nested_key in value_map:
                        setattr(group_obj, group_field.name, value_map[nested_key])
            else:
                root_key = field.name
                if root_key in value_map:
                    setattr(reconstructed_obj, root_key, value_map[root_key])

        self._dataclass_value = reconstructed_obj
        return reconstructed_obj
    
    def api_info(self) -> Dict[str, Any]:
        """
        Provides API information for the component for use in API docs.
        """
        return {"type": "object", "description": "A key-value dictionary of property settings."}

    def example_payload(self) -> Any:
        """
        Returns an example payload for the component's API.
        """
        return {"seed": 12345}