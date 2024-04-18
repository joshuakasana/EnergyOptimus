document.addEventListener("DOMContentLoaded", function() {
    // Get the modal
    var profileModal = document.getElementById("profileModal");

    // Get the button that opens the ChangeExpense modal
    var profileBtn = document.getElementById("profileButton");


    // When the user clicks on the changeExp button, open the changeExp modal
    profileBtn.onclick = function() {
        profileModal.style.display = "block";
    }


    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == profileModal) {
            profileModal.style.display = "none";
        }
    }
});
