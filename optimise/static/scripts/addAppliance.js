document.addEventListener("DOMContentLoaded", function() {
    // Get the modal
    var addApplianceModal = document.getElementById("addApplianceModal");

    // Get the button that opens the ChangeExpense modal
    var addApplianceBtn = document.getElementById("add-appliance-btn");


    // When the user clicks on the changeExp button, open the changeExp modal
    addApplianceBtn.onclick = function() {
        addApplianceModal.style.display = "block";
    }


    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == addApplianceModal) {
            addApplianceModal.style.display = "none";
        }
    }
});
