// Get the modal
var settingsModal = document.getElementById("settingsModal");

// Get the button that opens the settings modal
var settingsBtn = document.getElementById("settingsButton");

// Get the <span> elements that close the modals
var settingsCloseBtn = document.getElementById("settingsClose");

// When the user clicks on the settings button, open the settings modal
settingsBtn.onclick = function() {
    settingsModal.style.display = "block";
}

// When the user clicks on <span> (x), close the settings modal
settingsCloseBtn.onclick = function() {
    settingsModal.style.display = "none";
}

// When the user clicks anywhere outside of the modals, close them
window.onclick = function(event) {
    if (event.target == settingsModal) {
        settingsModal.style.display = "none";
    }
}
