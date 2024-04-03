// Get the modal
var settingsModal = document.getElementById("settingsModal");
var profileModal = document.getElementById("profileModal");

// Get the button that opens the settings modal
var settingsBtn = document.getElementById("settingsButton");
// Get the button that opens the profile modal
var profileBtn = document.getElementById("profileButton");

// Get the <span> elements that close the modals
var settingsCloseBtn = document.getElementById("settingsClose");
var profileCloseBtn = document.getElementById("profileClose");

// When the user clicks on the settings button, open the settings modal
settingsBtn.onclick = function() {
    settingsModal.style.display = "block";
}

// When the user clicks on the profile button, open the profile modal
profileBtn.onclick = function() {
    profileModal.style.display = "block";
}

// When the user clicks on <span> (x), close the settings modal
settingsCloseBtn.onclick = function() {
    settingsModal.style.display = "none";
}

// When the user clicks on <span> (x), close the profile modal
profileCloseBtn.onclick = function() {
    profileModal.style.display = "none";
}

// When the user clicks anywhere outside of the modals, close them
window.onclick = function(event) {
    if (event.target == settingsModal) {
        settingsModal.style.display = "none";
    }
    if (event.target == profileModal) {
        profileModal.style.display = "none";
    }
}
