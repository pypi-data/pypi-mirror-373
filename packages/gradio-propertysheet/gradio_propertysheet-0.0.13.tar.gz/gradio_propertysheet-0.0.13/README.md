---
tags: [gradio-custom-component, ui, form, settings, dataclass]
title: gradio_propertysheet
short_description: Property Sheet Component for Gradio
colorFrom: blue
colorTo: green
sdk: gradio
pinned: true
app_file: space.py
---

# `gradio_propertysheet`
<a href="https://pypi.org/project/gradio_propertysheet/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_propertysheet"></a>  

Property sheet

## Installation

```bash
pip install gradio_propertysheet
```

## Usage

```python
import os
import json
import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import Literal
from gradio_propertysheet import PropertySheet
from gradio_htmlinjector import HTMLInjector


# --- 1. Dataclass Definitions (unchanged) ---
@dataclass
class APISettings:
    api_key: str = field(
        default="ab123cd45ef67890ghij123klmno456p",
        metadata={
            "label": "API Key",            
            "component": "password", 
            "help": "Your secret API key. It will not be displayed."
        }
    )
    endpoint_url: str = field(
        default="https://api.example.com",
        metadata={
            "label": "API Endpoint",
            "component": "string", # string normal
            "help": "The URL of the API server."
        }
    )

@dataclass
class QuantizationSettings:
    quantization_method: Literal["None", "Quanto Library", "Layerwise & Bnb"] = field(
        default="Layerwise & Bnb",
        metadata={
            "component": "radio",
            "label": "Quantization Method",
            "help": "Quantization mechanism to save VRAM and increase speed."
        }
    )
    # Option 1: Literal values
    quantize_mode_list: Literal["FP8", "INT8", "IN4"] = field(
        default="FP8",
        metadata={
            "interactive_if": {"field": "quantization_method", "value": ["Quanto Library", "Layerwise & Bnb"]},
            "component": "radio",
            "label": "Quantization Mode (List)",
            "help": "This becomes interactive if Quantization Method is 'Quanto' OR 'Layerwise'."
        }
    )
    # Option 2: neq operand
    quantize_mode_neq: Literal["FP8", "INT8", "IN4"] = field(
        default="FP8",
        metadata={
            "interactive_if": {"field": "quantization_method", "neq": "None"},
            "component": "radio",
            "label": "Quantization Mode (Not Equal)",
            "help": "This becomes interactive if Quantization Method is NOT 'None'."
        }
    )
@dataclass
class ModelSettings:
    model_type: Literal["SD 1.5", "SDXL", "Pony", "Custom"] = field(
        default="SDXL",
        metadata={
            "component": "dropdown",
            "label": "Base Model",
            "help": "Select the base diffusion model."
        }
    )
    custom_model_path: str = field(
        default="/path/to/default.safetensors",
        metadata={
            "label": "Custom Model Path",
            "interactive_if": {"field": "model_type", "value": "Custom"},
            "help": "Provide the local file path to your custom .safetensors or .ckpt model file. This is only active when 'Base Model' is set to 'Custom'."
        },
    )
    vae_path: str = field(
        default="",
        metadata={
            "label": "VAE Path (optional)",
            "help": "Optionally, provide a path to a separate VAE file to improve color and detail."
        }
    )

@dataclass
class SamplingSettings:
    scheduler: Literal["Karras", "Simple", "Exponential"] = field(
        default="Karras",
        metadata={
            "component": "radio",
            "label": "Scheduler",
            "help": "Determines how the noise schedule is interpreted during sampling. 'Karras' is often recommended for high-quality results."
        }
    )
    sampler_name: Literal["Euler", "Euler a", "DPM++ 2M Karras", "UniPC"] = field(
        default="DPM++ 2M Karras",
        metadata={
            "component": "dropdown",
            "label": "Sampler",
            "help": "The algorithm used to denoise the image over multiple steps. Different samplers can produce stylistically different results."
        }
    )
    steps: int = field(
        default=25,
        metadata={
            "component": "slider",
            "label": "Sampling Steps",
            "minimum": 1,
            "maximum": 150,
            "step": 1,
            "help": "The number of denoising steps. More steps can increase detail but also take longer. Values between 20-40 are common."
        }
    )
    cfg_scale: float = field(
        default=7.0,
        metadata={
            "component": "slider",
            "label": "CFG Scale",
            "minimum": 1.0,
            "maximum": 30.0,
            "step": 0.5,
            "help": "Classifier-Free Guidance Scale. Higher values make the image adhere more strictly to the prompt, while lower values allow for more creativity."
        }
    )
    enable_advanced: bool = field(
        default=False,
        metadata={
            "label": "Enable Advanced Settings",
            "help": "Check this box to reveal more experimental or fine-tuning options."
        }
    )
    advanced_option: float = field(
        default=0.5,
        metadata={
            "label": "Advanced Option",
            "component": "slider",
            "minimum": 0.0,
            "maximum": 1.0,
            "step": 0.01,
            "interactive_if": {"field": "enable_advanced", "value": True},
            "help": "An example of an advanced setting that is only visible when the corresponding checkbox is enabled."
        },
    )
    temperature: float = field(
        default=1.0,
        metadata={
            "label": "Sampling Temperature",
            "component": "number_float",
            "minimum": 0.1,
            "maximum": 2.0,
            "step": 0.1,
            "help": "Controls the randomness of the sampling process. A value of 1.0 is standard. Higher values increase diversity at the risk of artifacts."
        }
    )

@dataclass
class RenderConfig:
    api_settings: APISettings = field(
        default_factory=APISettings,
        metadata={"label": "API Settings"}
    )
    randomize_seed: bool = field(
        default=True,
        metadata={
            "label": "Randomize Seed",
            "help": "If checked, a new random seed will be used for each generation. Uncheck to use the specific seed value below."
        }
    )
    seed: int = field(
        default=-1,
        metadata={
            "component": "number_integer",
            "label": "Seed",
            "help": "The seed for the random number generator. A value of -1 means a random seed will be chosen. The same seed and settings will produce the same image."
        }
    )
    model: ModelSettings = field(
        default_factory=ModelSettings,
        metadata={"label": "Model Settings"}
    )
    sampling: SamplingSettings = field(
        default_factory=SamplingSettings,
        metadata={"label": "Sampling Settings"}
    )
    quantization: QuantizationSettings = field(
        default_factory=QuantizationSettings,
        metadata={"label": "Quantization Settings"}
    )

@dataclass
class Lighting:
    sun_intensity: float = field(
        default=1.0,
        metadata={
            "component": "slider",
            "label": "Sun Intensity",
            "minimum": 0,
            "maximum": 5,
            "step": 0.1,
            "help": "Controls the brightness of the main light source in the scene."
        }
    )
    color: str = field(
        default="#FFDDBB",
        metadata={
            "component": "colorpicker",
            "label": "Sun Color",
            "help": "Sets the color of the main light source."
        }
    )

@dataclass
class EnvironmentConfig:
    background: Literal["Sky", "Color", "Image"] = field(
        default="Sky",
        metadata={
            "component": "dropdown",
            "label": "Background Type",
            "help": "Choose the type of background for the environment."
        }
    )
    lighting: Lighting = field(
        default_factory=Lighting,
        metadata={"label": "Lighting"}
    )

@dataclass
class EulerSettings:
    s_churn: float = field(
        default=0.0,
        metadata={
            "component": "slider",
            "label": "S_Churn",
            "minimum": 0.0,
            "maximum": 1.0,
            "step": 0.01,
            "help": "Stochasticity churn factor for Euler samplers. Adds extra noise at each step, affecting diversity. 0.0 is deterministic."
        }
    )

@dataclass
class DPM_Settings:
    karras_style: bool = field(
        default=True,
        metadata={
            "label": "Use Karras Sigma Schedule",
            "help": "If checked, uses the Karras noise schedule, which is often recommended for DPM++ samplers to improve image quality, especially in later steps."
        }
    )

# --- 2. Data Mappings and Initial Instances (unchanged) ---
initial_render_config = RenderConfig()
initial_env_config = EnvironmentConfig()
sampler_settings_map_py = {
    "Euler": EulerSettings(),
    "DPM++ 2M Karras": DPM_Settings(),
    "UniPC": None,
    "CustomSampler": SamplingSettings()
}
model_settings_map_py = {
    "SDXL 1.0": DPM_Settings(),
    "Stable Diffusion 1.5": EulerSettings(),
    "Pony": None,
}


# --- 3. CSS & JS Injection function (unchanged) ---
def inject_assets():
    """
    This function prepares the payload of CSS, JS, and Body HTML for injection.
    """
    popup_html = """<div id="injected_flyout_container" class="flyout-sheet" style="display: none;"></div>"""
    css_code = ""
    js_code = ""

    try:
        with open("custom.css", "r", encoding="utf-8") as f:
            css_code += f.read() + "\n"
        with open("custom.js", "r", encoding="utf-8") as f:
            js_code += f.read() + "\n"
    except FileNotFoundError as e:
        print(f"Warning: Could not read asset file: {e}")
    return {"js": js_code, "css": css_code, "body_html": popup_html}


# --- 4. Gradio App Build ---
with gr.Blocks(theme=gr.themes.Ocean(), title="PropertySheet Demos") as demo:
    html_injector = HTMLInjector()
    gr.Markdown("# PropertySheet Component Demos")

    with gr.Row():
        # --- Flyout popup ---
        with gr.Column(
            elem_id="flyout_panel_source", elem_classes=["flyout-source-hidden"]
        ) as flyout_panel_source:
            close_btn = gr.Button("×", elem_classes=["flyout-close-btn"])
            flyout_sheet = PropertySheet(
                visible=True,
                container=False,
                label="Settings",
                show_group_name_only_one=False,
                disable_accordion=True,
            )

    with gr.Tabs():
        with gr.TabItem("Original Sidebar Demo"):
            gr.Markdown(
                "An example of using the `PropertySheet` component as a traditional sidebar for settings."
            )
            render_state = gr.State(value=initial_render_config)
            env_state = gr.State(value=initial_env_config)
            sidebar_visible = gr.State(False)
            with gr.Row():
                with gr.Column(scale=3):
                    generate = gr.Button("Show Settings", variant="primary")
                    with gr.Row():
                        output_render_json = gr.JSON(label="Live Render State")
                        output_env_json = gr.JSON(label="Live Environment State")
                with gr.Column(scale=1):
                    render_sheet = PropertySheet(
                        value=initial_render_config,
                        label="Render Settings",
                        width=400,
                        height=550,
                        visible=False,
                        root_label="Generator",
                        interactive=True                        
                    )
                    environment_sheet = PropertySheet(
                        value=initial_env_config,
                        label="Environment Settings",
                        width=400,
                        open=False,
                        visible=False,
                        root_label="General",
                        interactive=True,
                        root_properties_first=False
                    )

            def change_visibility(is_visible, render_cfg, env_cfg):
                new_visibility = not is_visible
                button_text = "Hide Settings" if new_visibility else "Show Settings"
                return (
                    new_visibility,
                    gr.update(visible=new_visibility, value=render_cfg),
                    gr.update(visible=new_visibility, value=env_cfg),
                    gr.update(value=button_text),
                )

            def handle_render_change(
                updated_config: RenderConfig, current_state: RenderConfig
            ):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                if updated_config.model.model_type != "Custom":
                    updated_config.model.custom_model_path = "/path/to/default.safetensors"                
                return updated_config, asdict(updated_config), updated_config

            def handle_env_change(
                updated_config: EnvironmentConfig, current_state: EnvironmentConfig
            ):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                return updated_config, asdict(updated_config), current_state

            generate.click(
                fn=change_visibility,
                inputs=[sidebar_visible, render_state, env_state],
                outputs=[sidebar_visible, render_sheet, environment_sheet, generate],
            )
            render_sheet.change(
                fn=handle_render_change,
                inputs=[render_sheet, render_state],
                outputs=[render_sheet, output_render_json, render_state],
            )
            environment_sheet.change(
                fn=handle_env_change,
                inputs=[environment_sheet, env_state],
                outputs=[environment_sheet, output_env_json, env_state],
            )
            
            #In version 0.0.7, I moved the undo function to a new `undo` event. This was necessary to avoid conflict with the `change` event where it was previously implemented. 
            # Now you need to implement the undo event for the undo button to work. You can simply receive the component as input and set it as output.
            def render_undo(updated_config: RenderConfig, current_state: RenderConfig):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                return updated_config, asdict(updated_config), current_state
            
            def environment_undo(updated_config: EnvironmentConfig, current_state: EnvironmentConfig):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                return updated_config, asdict(updated_config), current_state
            
            render_sheet.undo(fn=render_undo, 
                              inputs=[render_sheet, render_state], 
                              outputs=[render_sheet, output_render_json, render_state]
            )
            environment_sheet.undo(fn=environment_undo, 
                            inputs=[environment_sheet, env_state],
                            outputs=[environment_sheet, output_env_json, env_state],
            )
            
            
            demo.load(
                fn=lambda r_cfg, e_cfg: (asdict(r_cfg), asdict(e_cfg)),
                inputs=[render_state, env_state],
                outputs=[output_render_json, output_env_json],
            )

        with gr.TabItem("Flyout Popup Demo"):
            gr.Markdown(
                "An example of attaching a `PropertySheet` as a flyout panel to other components."
            )

            # --- State Management ---
            flyout_visible = gr.State(False)
            active_anchor_id = gr.State(None)
            js_data_bridge = gr.Textbox(visible=False, elem_id="js_data_bridge")

            with gr.Column(elem_classes=["flyout-context-area"]):
                with gr.Row(
                    elem_classes=["fake-input-container", "no-border-dropdown"]
                ):
                    sampler_dd = gr.Dropdown(
                        choices=list(sampler_settings_map_py.keys()),
                        label="Sampler",
                        value="Euler",
                        elem_id="sampler_dd",
                        scale=10,
                    )
                    sampler_ear_btn = gr.Button(
                        "⚙️",
                        elem_id="sampler_ear_btn",
                        scale=1,
                        elem_classes=["integrated-ear-btn"],
                    )

                with gr.Row(
                    elem_classes=["fake-input-container", "no-border-dropdown"]
                ):
                    model_dd = gr.Dropdown(
                        choices=list(model_settings_map_py.keys()),
                        label="Model",
                        value="SDXL 1.0",
                        elem_id="model_dd",
                        scale=10,
                    )
                    model_ear_btn = gr.Button(
                        "⚙️",
                        elem_id="model_ear_btn",
                        scale=1,
                        elem_classes=["integrated-ear-btn"],
                    )

            # --- Event Logic ---
            def handle_flyout_toggle(
                is_vis, current_anchor, clicked_dropdown_id, settings_obj
            ):
                if is_vis and current_anchor == clicked_dropdown_id:
                    js_data = json.dumps({"isVisible": False, "anchorId": None})
                    return False, None, gr.update(), gr.update(value=js_data)
                else:
                    js_data = json.dumps(
                        {"isVisible": True, "anchorId": clicked_dropdown_id}
                    )
                    return (
                        True,
                        clicked_dropdown_id,
                        gr.update(value=settings_obj),
                        gr.update(value=js_data),
                    )

            def update_ear_visibility(selection, settings_map):
                has_settings = settings_map.get(selection) is not None
                return gr.update(visible=has_settings)

            def on_flyout_change(updated_settings, active_id, sampler_val, model_val):
                if updated_settings is None or active_id is None:
                    return
                if active_id == sampler_dd.elem_id:
                    sampler_settings_map_py[sampler_val] = updated_settings
                elif active_id == model_dd.elem_id:
                    model_settings_map_py[model_val] = updated_settings

            def close_the_flyout():
                js_data = json.dumps({"isVisible": False, "anchorId": None})
                return False, None, gr.update(value=js_data)

            js_update_flyout = "(jsonData) => { update_flyout_from_state(jsonData); }"

            sampler_dd.change(
                fn=lambda sel: update_ear_visibility(sel, sampler_settings_map_py),
                inputs=[sampler_dd],
                outputs=[sampler_ear_btn],
            ).then(
                fn=close_the_flyout,
                outputs=[flyout_visible, active_anchor_id, js_data_bridge],
            ).then(
                fn=None, inputs=[js_data_bridge], js=js_update_flyout
            )

            sampler_ear_btn.click(
                fn=lambda is_vis, anchor, sel: handle_flyout_toggle(
                    is_vis, anchor, sampler_dd.elem_id, sampler_settings_map_py.get(sel)
                ),
                inputs=[flyout_visible, active_anchor_id, sampler_dd],
                outputs=[
                    flyout_visible,
                    active_anchor_id,
                    flyout_sheet,
                    js_data_bridge,
                ],
            ).then(fn=None, inputs=[js_data_bridge], js=js_update_flyout)

            model_dd.change(
                fn=lambda sel: update_ear_visibility(sel, model_settings_map_py),
                inputs=[model_dd],
                outputs=[model_ear_btn],
            ).then(
                fn=close_the_flyout,
                outputs=[flyout_visible, active_anchor_id, js_data_bridge],
            ).then(
                fn=None, inputs=[js_data_bridge], js=js_update_flyout
            )

            model_ear_btn.click(
                fn=lambda is_vis, anchor, sel: handle_flyout_toggle(
                    is_vis, anchor, model_dd.elem_id, model_settings_map_py.get(sel)
                ),
                inputs=[flyout_visible, active_anchor_id, model_dd],
                outputs=[
                    flyout_visible,
                    active_anchor_id,
                    flyout_sheet,
                    js_data_bridge,
                ],
            ).then(fn=None, inputs=[js_data_bridge], js=js_update_flyout)

            flyout_sheet.change(
                fn=on_flyout_change,
                inputs=[flyout_sheet, active_anchor_id, sampler_dd, model_dd],
                outputs=None,
            )

            close_btn.click(
                fn=close_the_flyout,
                inputs=None,
                outputs=[flyout_visible, active_anchor_id, js_data_bridge],
            ).then(fn=None, inputs=[js_data_bridge], js=js_update_flyout)

            def initial_flyout_setup(sampler_val, model_val):
                return {
                    sampler_ear_btn: update_ear_visibility(
                        sampler_val, sampler_settings_map_py
                    ),
                    model_ear_btn: update_ear_visibility(
                        model_val, model_settings_map_py
                    ),
                }

            # --- App Load ---
            demo.load(fn=inject_assets, inputs=None, outputs=[html_injector]).then(
                fn=initial_flyout_setup,
                inputs=[sampler_dd, model_dd],
                outputs=[sampler_ear_btn, model_ear_btn],
            ).then(
                fn=None,
                inputs=None,
                outputs=None,
                js="() => { setTimeout(reparent_flyout, 200); }",
            )

if __name__ == "__main__":
    demo.launch()

```

## `PropertySheet`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[typing.Any][Any, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The initial dataclass instance to render.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The main label for the component, displayed in the accordion header.</td>
</tr>

<tr>
<td align="left"><code>root_label</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"General"</code></td>
<td align="left">The label for the root group of properties.</td>
</tr>

<tr>
<td align="left"><code>show_group_name_only_one</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, only the group name is shown when there is a single group.</td>
</tr>

<tr>
<td align="left"><code>root_properties_first</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True (default), root-level properties are rendered before nested groups. If False, they are rendered after.</td>
</tr>

<tr>
<td align="left"><code>disable_accordion</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, disables the accordion functionality.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>open</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the accordion will be collapsed by default.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the DOM.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The relative size of the component in its container.</td>
</tr>

<tr>
<td align="left"><code>width</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The width of the component in pixels.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The maximum height of the component's content area in pixels before scrolling.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The minimum width of the component in pixels.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, wraps the component in a container with a background.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the DOM.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the PropertySheet changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the PropertySheet. |
| `expand` | This listener is triggered when the PropertySheet is expanded. |
| `collapse` | This listener is triggered when the PropertySheet is collapsed. |
| `undo` | This listener is triggered when the user clicks the undo button in component. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, a new, updated instance of the dataclass.
- **As input:** Should return, the dataclass instance to process.

 ```python
 def predict(
     value: Any
 ) -> Any:
     return value
 ```
 
