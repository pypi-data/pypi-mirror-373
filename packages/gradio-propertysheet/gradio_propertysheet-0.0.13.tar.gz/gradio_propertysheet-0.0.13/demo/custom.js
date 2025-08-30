function reparent_flyout() {
    //console.log("Attempting to reparent flyout...");
    const source = document.getElementById('flyout_panel_source');
    const target = document.getElementById('injected_flyout_container');
    
    if (source && target) {
        while (source.firstChild) {
            target.appendChild(source.firstChild);
        }
        source.remove();
        //console.log("SUCCESS: Flyout panel has been reparented.");
    } else {
        console.error("ERROR: Reparenting failed. Source or target element not found.");
    }
}

function position_flyout(anchorId) {
    if (!anchorId) {
         return; 
    }
    
    const anchorElem = document.getElementById(anchorId);
    const flyoutElem = document.getElementById('injected_flyout_container');
    
    if (anchorElem && flyoutElem) {
        //console.log("JS: Positioning flyout relative to:", anchorId);
        const anchorRect = anchorElem.getBoundingClientRect();
        const flyoutWidth = flyoutElem.offsetWidth;
        const flyoutHeight = flyoutElem.offsetHeight;

        let topPosition = anchorRect.top + (anchorRect.height / 2) - (flyoutHeight / 2);
        let leftPosition = anchorRect.left + (anchorRect.width / 2) - (flyoutWidth / 2);
        
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        if (leftPosition < 8) leftPosition = 8;
        if (topPosition < 8) topPosition = 8;
        if (leftPosition + flyoutWidth > windowWidth) leftPosition = windowWidth - flyoutWidth - 8;
        if (topPosition + flyoutHeight > windowHeight) topPosition = windowHeight - flyoutHeight - 8;

        flyoutElem.style.top = `${topPosition}px`;
        flyoutElem.style.left = `${leftPosition}px`;
    }
}

// This is the new main function called by Gradio's .then() event
function update_flyout_from_state(jsonData) {
    //console.log("JS: update_flyout_from_state() called with data:", jsonData);
    
    if (!jsonData) return;
 
    const state = JSON.parse(jsonData);
    const { isVisible, anchorId } = state;
    const flyout = document.getElementById('injected_flyout_container');

    if (!flyout) {
        console.error("ERROR: Cannot update UI. Flyout container not found.");
        return;
    }

    //console.log("JS: Parsed state:", { isVisible, anchorId });

    if (isVisible) {
        flyout.style.display = 'flex';
        position_flyout(anchorId);
    } else {
        flyout.style.display = 'none';
    }
}