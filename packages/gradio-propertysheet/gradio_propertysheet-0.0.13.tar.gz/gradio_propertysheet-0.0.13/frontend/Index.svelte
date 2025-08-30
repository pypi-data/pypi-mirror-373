<script lang="ts">
    // --- Imports ---
    import { Block } from "@gradio/atoms";
    import { StatusTracker } from "@gradio/statustracker";
    import type { LoadingStatus } from "@gradio/statustracker";
    import type { Gradio } from "@gradio/utils";
    import { onMount, tick } from "svelte";

    // --- Component Props (passed from Gradio backend) ---
    /** The main data structure driving the UI, an array of property groups. */
    export let value: Array<{ group_name: string, properties: any[] }> = [];
    /** The main label for the component, displayed in the top-level accordion header. */
    export let label: string | undefined = undefined;
    /** The label for the root group of properties, displayed when there is only one group. */
    export let show_group_name_only_one: boolean = true;
    /** If true, disables the accordion functionality, showing all properties without grouping. */
    export let disable_accordion: boolean = false;
    /** Controls the overall visibility of the component. */
    export let visible: boolean = true;
    /** If true, the main accordion is open by default. */
    export let open: boolean = true;
    /** The DOM element ID. */
    export let elem_id: string = "";
    /** Custom CSS classes for the root element. */
    export let elem_classes: string[] = [];
    /** If true, wraps the component in a container with a background. */
    export let container: boolean = false;
    /** The relative size of the component in its container. */
    export let scale: number | null = null;
    /** The minimum width of the component in pixels. */
    export let min_width: number | undefined = undefined;
    /** The fixed width of the component in pixels. */
    export let width: number | undefined = undefined;
    /** The maximum height of the component's content area before scrolling. */
    export let height: number | undefined = undefined;
    /** The loading status object from Gradio. */
    export let loading_status: LoadingStatus | undefined = undefined;
    /** If false, all controls are disabled. */
    export let interactive: boolean = true;
    /** The Gradio event dispatcher instance. */
    export let gradio: Gradio<{ change: any, reset: any, input: any, clear_status: never, expand: never, collapse: never, undo: any }>;

    // --- Internal State ---
    /** Tracks the open/closed state of each individual property group. */
    let groupVisibility: Record<string, boolean> = {};
    /** Holds references to slider input elements for direct DOM manipulation (e.g., setting background). */
    let sliderElements: Record<string, HTMLInputElement> = {};
    /** Combines default and user-provided CSS classes. */
    $: final_classes = ["propertysheet-wrapper", ...elem_classes];
    /** Tracks the validation status (true/false) for each property to apply error styling. */
    let validationState: Record<string, boolean> = {};
    /** A stringified version of the `value` prop, used to detect changes from the backend. */
    let lastValue: string | null = null;
    /** A flag to prevent event loops during property reset operations. */
    let isResetting: boolean = false;
    /** A snapshot of the initial values of all properties, used for the reset functionality. */
    let initialValues: Record<string, any> = {};

    /**
     * Validates a numeric property against its `minimum` and `maximum` constraints.
     * Updates the `validationState` for CSS styling of invalid inputs.
     * @param {any} prop - The property object to validate.
     */
    function validate_prop(prop: any) {
        if (prop.minimum === undefined && prop.maximum === undefined) {
            if (validationState[prop.name] !== true) {
                validationState[prop.name] = true;
                validationState = { ...validationState };
            }
            return;
        }
        const numValue = Number(prop.value);
        let is_valid = true;
        if (prop.minimum !== undefined && numValue < prop.minimum) is_valid = false;
        if (prop.maximum !== undefined && numValue > prop.maximum) is_valid = false;
        if (validationState[prop.name] !== is_valid) {
            validationState[prop.name] = is_valid;
            validationState = { ...validationState };
        }
    }

    /** Controls the component's content height based on the main accordion's open/closed state. */
    let dynamic_height: number | undefined;
    $: dynamic_height = open ? height : undefined;

    /**
     * Iterates through all properties and updates the background visuals of any sliders.
     */
    function updateAllSliders() {
        if (!Array.isArray(value)) return;
        for (const group of value) {
            if (Array.isArray(group.properties)) {
                for (const prop of group.properties) {
                    if (prop.component === 'slider' && sliderElements[prop.name]) {
                        updateSliderBackground(prop, sliderElements[prop.name]);
                    }
                }
            }
        }
    }

    /**
     * Reactive block that triggers whenever the `value` prop changes from the backend.
     * It initializes group visibility, validates properties, and updates slider visuals.
     */
    $: if (Array.isArray(value) && JSON.stringify(value) !== lastValue) {
        lastValue = JSON.stringify(value);
        for (const group of value) {
            if (groupVisibility[group.group_name] === undefined) {
                groupVisibility[group.group_name] = true;
            }
            if (Array.isArray(group.properties)) {
                for (const prop of group.properties) {
                    if (prop.component?.startsWith("number") || prop.component === 'slider') {
                        validate_prop(prop);
                    }
                }
            }
        }
        updateAllSliders();
    }
    
    /**
     * Updates a slider's track background to visually represent its value as a percentage.
     * It sets the `--slider-progress` CSS custom property.
     * @param {any} prop - The slider property object.
     * @param {HTMLInputElement} element - The slider's input element.
     */
    function updateSliderBackground(prop: any, element: HTMLInputElement) {
        if (!element) return;
        const min = prop.minimum ?? 0;
        const max = prop.maximum ?? 100;
        const val = Number(prop.value);
        const percentage = val <= min ? 0 : ((val - min) * 100) / (max - min);
        element.style.setProperty('--slider-progress', `${percentage}%`);
    }

    /**
     * Handles the main accordion toggle (the component's top-level header).
     * Dispatches 'expand' or 'collapse' events to Gradio.
     */
    function handle_toggle() {        
        open = !open;
        if (open) gradio.dispatch("expand");
        else gradio.dispatch("collapse");
    }

    /**
     * Toggles the visibility of an individual property group (e.g., "Model", "Sampling").
     * @param {string} groupName - The name of the group to toggle.
     */
    function toggleGroup(groupName: string) {
        groupVisibility[groupName] = !groupVisibility[groupName];
    }
    
    /**
     * Utility function to find the current value of a specific property by its name.
     * Used to implement the `interactive_if` logic.
     * @param {string} prop_name - The name of the property to find.
     */
    function get_prop_value(prop_name: string) {
        if (!Array.isArray(value)) return undefined;
        for (const group of value) {
            if (!Array.isArray(group.properties)) continue;
            const found_prop = group.properties.find(p => p.name === prop_name);
            if (found_prop) return found_prop.value;
        }
        return undefined;
    }

    /**
     * Dispatches a single-property update to the Gradio backend.
     * Used for simple inputs like textboxes, sliders, and checkboxes.
     * Creates a small payload like `{ 'prop_name': new_value }`.
     * @param {"change" | "input"} event_name - The type of event to dispatch.
     * @param {any} changed_prop - The property object that was modified.
     */
    function dispatch_update(event_name: "change" | "input", changed_prop: any) {
        if (validationState[changed_prop.name] === false) {
            return;
        }
        const payload: Record<string, any> = {};
        let final_value = changed_prop.value;
        if (changed_prop.component?.startsWith("number") || changed_prop.component === "slider") {
            final_value = Number(changed_prop.value);
        } else if (changed_prop.component === "checkbox") {
            final_value = changed_prop.value;
        }
        payload[changed_prop.name] = final_value;
        gradio.dispatch(event_name, payload);
    }
    
    /**
     * Handles changes from a dropdown (`select`) element.
     * It updates the local `value` array and then dispatches the *entire updated object*
     * to the backend. This is a robust way to ensure state consistency.
     * @param {Event} event - The DOM change event.
     * @param {any} prop_to_change - The property object being modified.
     */
    async function handle_dropdown_change(event: Event, prop_to_change: any) {
        const new_prop_value = (event.target as HTMLSelectElement).value;

        // Recreate the entire `value` array to ensure Svelte's reactivity.
        value = value.map(group => {
            if (!group.properties) return group;
            return {
                ...group,
                properties: group.properties.map(prop => {
                    if (prop.name === prop_to_change.name) {
                        return { ...prop, value: new_prop_value };
                    }
                    return prop;
                })
            };
        });

        // Wait for Svelte to process the DOM update before dispatching.
        await tick();
        // Dispatch the full, updated value object to the backend.
        gradio.dispatch("change", value);
    }

    /**
     * Resets a single property to its initial value, which was stored on mount.
     * It dispatches the entire updated `value` object to the backend.
     * @param {string} propName - The name of the property to reset.
     */
    function handle_reset_prop(propName: string) {
        if (isResetting) return;
        isResetting = true;
        if (!(propName in initialValues)) {
            isResetting = false;
            return;
        }
        let updatedValue = value.map(group => {
            if (group.properties) {
                group.properties = group.properties.map(prop => {
                    if (prop.name === propName) {
                        return { ...prop, value: initialValues[propName] };
                    }
                    return prop;
                });
            }
            return group;
        });
        value = updatedValue;
        gradio.dispatch("undo", updatedValue);
        setTimeout(() => { isResetting = false; }, 100);
    }

    /**
     * Creates a snapshot of the initial values of all properties.
     * This snapshot is used by the reset functionality.
     */
    function storeInitialValues() {
        lastValue = JSON.stringify(value);
        if (Array.isArray(value)) {
            value.forEach(group => {
                if (Array.isArray(group.properties)) {
                    group.properties.forEach(prop => {
                        initialValues[prop.name] = prop.value;
                    });
                }
            });
        }
        
        // Ensure sliders are visually updated on initial load.
        setTimeout(updateAllSliders, 50);
    }

    /**
     * Lifecycle hook that runs when the component is first added to the DOM.
     */
    onMount(() => {       
        storeInitialValues();
    });
    $: if (open && groupVisibility) {     
        tick().then(updateAllSliders);
    }
</script>

<!-- The HTML template renders the component's UI based on the `value` prop. -->
<Block {visible} {elem_id} elem_classes={final_classes} {container} {scale} {min_width} {width}>
    {#if loading_status}
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
            on:clear_status={() => gradio.dispatch("clear_status")}
        />
    {/if}

    <!-- Main accordion header that toggles the entire component's content -->
    <button class="accordion-header" on:click={handle_toggle} disabled={disable_accordion}>
        {#if label}
            <span class="label">{label}</span>
        {/if}
        {#if !disable_accordion}
            <span class="accordion-icon" style:transform={open ? "rotate(0)" : "rotate(-90deg)"}>▼</span>
        {/if}        
    </button>
    
    <!-- Content wrapper that is shown or hidden based on the 'open' state -->
    <div class:closed={!open} class="content-wrapper">
        {#if open}
            <div class="container" style="--show-group-name: {value.length > 1 || (show_group_name_only_one && value.length === 1) ? 'none' : '1px solid var(--border-color-primary)'}; --sheet-max-height: {height ? `${height}px` : 'none'}">
                {#if Array.isArray(value)}
                    <!-- Loop through each property group -->
                    {#each value as group (group.group_name)}
                        {#if value.length > 1 || (show_group_name_only_one && value.length === 1)}
                            <button class="group-header" on:click={() => toggleGroup(group.group_name)}>
                                <span class="group-title">{group.group_name}</span>
                                <span class="group-toggle-icon">{groupVisibility[group.group_name] ? '−' : '+'}</span>
                            </button>
                        {/if}    
                        {#if groupVisibility[group.group_name]}
                            <div class="properties-grid">
                                <!-- Loop through each property within a group -->
                                {#if Array.isArray(group.properties)}
                                    {#each group.properties as prop (prop.name)}
                                        <!-- Conditional interactivity based on another property's value -->
                                        {@const condition = prop.interactive_if}
                                        {@const parent_value = condition ? get_prop_value(condition.field) : null}

                                        {@const is_interactive = interactive && (
                                            !condition ? 
                                                true // No condition, so it's interactive by default.
                                            :
                                            condition.value !== undefined ?
                                                // Case 1: `value` key exists (equality check)
                                                Array.isArray(condition.value) ?
                                                    // If `value` is an array, check if parent_value is IN the array.
                                                    condition.value.includes(parent_value)
                                                :
                                                    // If `value` is a single item, do a strict equality check.
                                                    parent_value === condition.value
                                            :
                                            condition.neq !== undefined ?
                                                // Case 2: `neq` key exists (inequality check)
                                                parent_value !== condition.neq
                                            :
                                                true // Fallback if `interactive_if` is malformed.
                                        )}

                                        <label class="prop-label" for={prop.name}>
                                            <div class="prop-label-wrapper">
                                                <span>{prop.label}</span>
                                                <!-- Help tooltip -->
                                                {#if prop.help}
                                                    <div class="tooltip-container">
                                                        <span class="tooltip-icon">?</span>
                                                        <span class="tooltip-text">{prop.help}</span>
                                                    </div>
                                                {/if}
                                            </div>
                                        </label>
                                        
                                        <div class="prop-control">
                                            <!-- Dynamically render the correct input component based on `prop.component` -->
                                            {#if prop.component === 'string'}
                                                <input 
                                                    type="text" 
                                                    bind:value={prop.value} 
                                                    disabled={!is_interactive} 
                                                    on:change={() => dispatch_update("change", prop)} 
                                                    on:input={() => dispatch_update("input", prop)} 
                                                />
                                            {:else if prop.component === 'password'}
                                                <input 
                                                    type="password" 
                                                    bind:value={prop.value} 
                                                    disabled={!is_interactive} 
                                                    on:change={() => dispatch_update("change", prop)} 
                                                    on:input={() => dispatch_update("input", prop)} 
                                                />
                                            {:else if prop.component === 'checkbox'}                                                
                                                <input                                                         
                                                    type="checkbox" 
                                                    bind:checked={prop.value} 
                                                    disabled={!is_interactive} 
                                                    on:change={() => dispatch_update("change", prop)} 
                                                />                                            
                                            {:else if prop.component === 'number_integer' || prop.component === 'number_float'}
                                                <input 
                                                    class:invalid={validationState[prop.name] === false}
                                                    class:disabled={!is_interactive}
                                                    type="number" 
                                                    step={prop.step || 1} 
                                                    bind:value={prop.value} 
                                                    disabled={!is_interactive} 
                                                    on:change={() => dispatch_update("change", prop)} 
                                                    on:input={() => {
                                                        validate_prop(prop);
                                                        dispatch_update("input", prop);
                                                    }}
                                                />
                                            {:else if prop.component === 'slider'}
                                                <div class="slider-container" class:disabled={!is_interactive}>
                                                    <input 
                                                        type="range" 
                                                        min={prop.minimum} 
                                                        max={prop.maximum} 
                                                        step={prop.step || 1} 
                                                        bind:value={prop.value} 
                                                        bind:this={sliderElements[prop.name]}
                                                        disabled={!is_interactive} 
                                                        on:input={() => {
                                                            validate_prop(prop);
                                                            updateSliderBackground(prop, sliderElements[prop.name]);
                                                            dispatch_update("input", prop);
                                                        }} 
                                                        on:change={() => dispatch_update("change", prop)} 
                                                    />
                                                    <span class="slider-value">{prop.value}</span>
                                                </div>										
                                            {:else if prop.component === 'colorpicker'}
                                                <div class="color-picker-container" class:disabled={!is_interactive}>
                                                    <input 
                                                        type="color" 
                                                        class="color-picker-input"
                                                        bind:value={prop.value}
                                                        disabled={!is_interactive}
                                                        on:change={() => dispatch_update("change", prop)}
                                                    />
                                                    <span class="color-picker-value">{prop.value}</span>
                                                </div>
                                            {:else if prop.component === 'dropdown'}
                                                <div class="dropdown-wrapper" class:disabled={!is_interactive}>
                                                    <select 
                                                        disabled={!is_interactive} 
                                                        value={prop.value}
                                                        on:change={(e) => handle_dropdown_change(e, prop)}
                                                    >
                                                        {#if Array.isArray(prop.choices)}
                                                            {#each prop.choices as choice}
                                                                <option value={choice} selected={prop.value === choice}>
                                                                    {choice}
                                                                </option>
                                                            {/each}
                                                        {/if}
                                                    </select>
                                                    <div class="dropdown-arrow-icon"></div>												
                                                </div>
                                            {:else if prop.component === 'radio'}
                                                <div class="radio-group" class:disabled={!is_interactive} on:change={() => dispatch_update('change', prop)}>
                                                    {#if Array.isArray(prop.choices)}
                                                        {#each prop.choices as choice}
                                                            <div class="radio-item">
                                                                <input 
                                                                    type="radio" 
                                                                    id="{prop.name}-{choice}" 
                                                                    name={prop.name}
                                                                    value={choice}
                                                                    bind:group={prop.value}
                                                                    disabled={!is_interactive}
                                                                >
                                                                <label for="{prop.name}-{choice}">{choice}</label>
                                                            </div>
                                                        {/each}
                                                    {/if}
                                                </div>
                                            {/if}

                                            <!-- Reset button, visible only when the current value differs from the initial value -->
                                            {#if prop.component !== 'checkbox'}
                                                <button 
                                                    class="reset-button-prop" 
                                                    class:visible={initialValues[prop.name] !== prop.value}
                                                    title="Reset to default" 
                                                    on:click|stopPropagation={() => handle_reset_prop(prop.name)}
                                                    disabled={!is_interactive}
                                                >
                                                    ↺
                                                </button>
                                            {/if}
                                        </div>
                                    {/each}
                                {/if}
                            </div>
                        {/if}
                    {/each}
                {/if}
            </div>
        {/if}
    </div>
</Block>

<style>
    /* All styles remain the same and are included for completeness */
    :host {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    :global(.propertysheet-wrapper) {
        overflow: hidden !important;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        padding: var(--spacing-lg) !important;
    }
    .accordion-header {    
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        cursor: pointer;
        padding: var(--block-title-padding);
        background: var(--block-title-background-fill);
        color: var(--block-title-text-color);
        border-width: 0;
        flex-shrink: 0;
    }
    .accordion-icon{
        margin-left: auto;
    }
    .content-wrapper {
        flex-grow: 1;
        min-height: 0;        
    }
    .container {
        overflow-y: auto;
        height: auto; 
        max-height: var(--sheet-max-height, 500px);
        border-radius: 0 !important;
        border: 1px solid var(--border-color-primary);
        border-top: var(--show-group-name);
        border-bottom-left-radius: var(--radius-lg);
        border-bottom-right-radius: var(--radius-lg);
        background-color: var(--background-fill-secondary);        
    }
    .closed {
        display: none;
    }
    .group-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        padding: var(--spacing-sm) var(--spacing-md);
        background-color: var(--input-background-fill);
        color: var(--body-text-color);
        text-align: left;
        cursor: pointer;
        font-size: var(--text-md);
        font-weight: var(--font-weight-bold);
        border: 1px solid var(--border-color-primary);
    }
    .properties-grid {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 0;
        padding: 0;
    }
    .prop-label,
    .prop-control {
        padding: var(--spacing-sm) var(--spacing-md);
        display: flex;
        align-items: center;
        border-bottom: 1px solid var(--background-fill-secondary);
    }
  
    .prop-label {
        background-color: var(--background-fill-primary);
        color: var(--body-text-color);
        opacity: 3.7;
        font-weight: var(--font-weight-semibold);
        font-size: var(--text-xs);
        text-align: right;
        justify-content: flex-end;
        word-break: break-word;
    }
    .prop-control {
        gap: var(--spacing-sm);
    }
    .properties-grid > :nth-last-child(-n+2) {
        border-bottom: none;
    }
    .prop-control input[type="text"],
    .prop-control input[type="password"],
    .prop-control input[type="number"] {
        background-color: var(--input-background-fill);
        border: var(--input-border-width) solid var(--border-color-primary);
        box-shadow: var(--input-shadow);
        color: var(--input-text-color);
        font-size: var(--input-text-size);
        border-radius: 0;
        width: 100%;
        padding-top: var(--spacing-1);
        padding-bottom: var(--spacing-1);
        padding-left: var(--spacing-md);
        padding-right: var(--spacing-3);
    }
    .prop-control input[type="text"]:focus,
    .prop-control input[type="number"]:focus {
        box-shadow: var(--input-shadow-focus);
        border-color: var(--input-border-color-focus);
        background-color: var(--input-background-fill-focus);
        outline: none;
    }
    .dropdown-wrapper {
        position: relative;
        width: 100%;
    }
    .dropdown-wrapper select {
        -webkit-appearance: none;
        appearance: none;
        background-color: var(--input-background-fill);
        border: var(--input-border-width) solid var(--border-color-primary);
        box-shadow: var(--input-shadow);
        color: var(--input-text-color);
        font-size: var(--input-text-size);
        width: 100%;
        cursor: pointer;
        border-radius: 0;
        padding-top: var(--spacing-1);
        padding-bottom: var(--spacing-1);
        padding-left: var(--spacing-md);
        padding-right: calc(var(--spacing-3) + 1.2em);
    }
    .dropdown-arrow-icon {
        position: absolute;
        top: 50%;
        right: var(--spacing-3);
        transform: translateY(-50%);
        width: 1em;
        height: 1em;
        pointer-events: none;
        z-index: 1;
        background-color: var(--body-text-color-subdued);
        -webkit-mask-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
        mask-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M6 8l4 4 4-4'%3e%3c/svg%3e");
    }
    .dropdown-wrapper select:focus {
        box-shadow: var(--input-shadow-focus);
        border-color: var(--input-border-color-focus);
        background-color: var(--input-background-fill-focus);
        outline: none;
    }
    .dropdown-wrapper select option {
        background: var(--input-background-fill);
        color: var(--body-text-color);
    }
    .prop-control input[type="checkbox"] {
        -webkit-appearance: none;
        appearance: none;
        position: relative;
        width: var(--size-4);
        height: var(--size-4);
        border-radius: 5px !important;
        border: 1px solid var(--checkbox-border-color);
        background-color: var(--checkbox-background-color);
        box-shadow: var(--checkbox-shadow);
        cursor: pointer;
        margin: 0;
        transition: background-color 0.2s, border-color 0.2s;
    }
    .prop-control input[type="checkbox"]:hover {
        border-color: var(--checkbox-border-color-hover);
        background-color: var(--checkbox-background-color-hover);
    }
    .prop-control input[type="checkbox"]:focus {
        border-color: var(--checkbox-border-color-focus);
        background-color: var(--checkbox-background-color-focus);
        outline: none;
    }
    .prop-control input[type="checkbox"]:checked {
        background-color: var(--checkbox-background-color-selected);
        border-color: var(--checkbox-border-color-focus);        
    }
    .prop-control input[type="checkbox"]:checked::after {
        content: "";
        position: absolute;
        display: block;
        top: 50%;
        left: 50%;
        width: 4px;
        height: 8px;
        border: solid var(--checkbox-label-text-color-selected);
        border-width: 0 2px 2px 0;
        transform: translate(-50%, -60%) rotate(45deg);
        
    }
    .slider-container {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        width: 100%;
    }
    .slider-container input[type="range"] {
        --slider-progress: 0%;
        -webkit-appearance: none;
        appearance: none;
        background: transparent;
        cursor: pointer;
        width: 100%;
    }
    .slider-container input[type="range"]::-webkit-slider-runnable-track {
        height: 8px;
        border-radius: var(--radius-lg);
        background: linear-gradient( to right, var(--slider-color) var(--slider-progress), var(--input-background-fill) var(--slider-progress) );
    }
    .slider-container input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        margin-top: -4px;
        background-color: white;
        border-radius: 50%;
        height: 16px;
        width: 16px;
        border: 1px solid var(--border-color-primary);
        box-shadow: var(--shadow-drop);
    }
    .slider-container input[type="range"]::-moz-range-track {
        height: 8px;
        border-radius: var(--radius-lg);
        background: linear-gradient( to right, var(--slider-color) var(--slider-progress), var(--input-background-fill) var(--slider-progress) );
    }
    .slider-container input[type="range"]::-moz-range-thumb {
        background-color: white;
        border-radius: 50%;
        height: 16px;
        width: 16px;
        border: 1px solid var(--border-color-primary);
        box-shadow: var(--shadow-drop);
    }
    .slider-value {
        min-width: 40px;
        text-align: right;
        font-family: var(--font-mono);
        font-size: var(--text-xs);
    }
    .prop-label-wrapper {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: var(--spacing-sm);
        width: 100%;
    }
    .tooltip-container {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .tooltip-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background-color: var(--body-text-color-subdued);
        color: var(--background-fill-primary);
        font-size: 10px;
        font-weight: bold;
        cursor: help;
        user-select: none;
    }
    .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: var(--body-text-color);
        color: var(--background-fill-primary);
        text-align: center;
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        position: absolute;
        z-index: 50;
        bottom: -50%;
        left: 50%;        
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip-container:hover .tooltip-text {
        visibility: visible;
        opacity: 1.0;
    }
	.color-picker-container {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		width: 100%;
	}
	.color-picker-input {
		width: 50px;
		height: 28px;
		background-color: transparent;
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-sm);
		cursor: pointer;
		padding: 0;
	}
	.color-picker-input::-webkit-color-swatch-wrapper {
		padding: 2px;
	}
	.color-picker-input::-moz-padding {
	    padding: 2px;
	}
	.color-picker-input::-webkit-color-swatch {
		border: none;
		border-radius: var(--radius-sm);
	}
	.color-picker-input::-moz-color-swatch {
		border: none;
		border-radius: var(--radius-sm);
	}
	.color-picker-value {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		color: var(--body-text-color-subdued);
	}
    .prop-control input.invalid {
        border-color: var(--error-border-color, red) !important;
        box-shadow: 0 0 0 1px var(--error-border-color, red) !important;
    }
    .reset-button-prop {
        display: flex;
        align-items: center;
        justify-content: center;
        background: none;
        border: none;
        border-left: 1px solid var(--border-color-primary);
        cursor: pointer;
        color: var(--body-text-color-subdued);
        font-size: var(--text-lg);
        padding: 0 var(--spacing-2);
        visibility: hidden;
        opacity: 0;
        transition: opacity 150ms ease-in-out, color 150ms ease-in-out;
    }
    .reset-button-prop.visible {
        visibility: visible;
        opacity: 1;
    }
    .reset-button-prop:hover {
        color: var(--body-text-color);
        background-color: var(--background-fill-secondary-hover);
    }
    .reset-button-prop:disabled {
	    color: var(--body-text-color-subdued) !important;
	    opacity: 0.5;
	    cursor: not-allowed;
	    background-color: transparent !important;
	}
    .prop-control .disabled {
		opacity: 0.5;
		pointer-events: none;
		cursor: not-allowed;
	}
	.prop-control .disabled input {
		cursor: not-allowed;
	}
	.reset-button-prop:disabled {
	    opacity: 0.3;
	    cursor: not-allowed;
	    background-color: transparent !important;
	}
    
    .radio-group {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-sm);
		width: 100%;
	}
	.radio-item input[type="radio"] {
		/* Hide the default radio button */
		display: none;
	}
	.radio-item label {
		display: inline-block;
		padding: var(--spacing-xs) var(--spacing-md);
		border: 1px solid var(--border-color-primary);
        border-radius: 5px !important;
		background-color: var(--input-background-fill);
		color: var(--body-text-color);
		font-size: var(--text-xs);
		cursor: pointer;
		user-select: none;
		transition: background-color 0.2s, border-color 0.2s, color 0.2s;
	}
	.radio-group.disabled .radio-item label {
		cursor: not-allowed;
	}
	.radio-item input[type="radio"]:hover + label {
		border-color: var(--border-color-accent-subdued);
		background-color: var(--background-fill-secondary-hover);
	}
	.radio-item input[type="radio"]:checked + label {
		background-color: var(--primary-500);
		border-color: var(--primary-500);
		color: white;
		font-weight: var(--font-weight-bold);
	}
	.radio-group.disabled .radio-item input[type="radio"]:checked + label {
		background-color: var(--neutral-300);
		border-color: var(--neutral-300);
		color: var(--neutral-500);
	}
</style>