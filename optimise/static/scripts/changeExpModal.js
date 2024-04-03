document.addEventListener("DOMContentLoaded", function() {
    // Get the modal
    var changeExpModal = document.getElementById("changeExpModal");

    // Get the button that opens the ChangeExpense modal
    var changeExpBtn = document.getElementById("changeExpButton");


    // When the user clicks on the changeExp button, open the changeExp modal
    changeExpBtn.onclick = function() {
        changeExpModal.style.display = "block";
    }


    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == changeExpModal) {
            changeExpModal.style.display = "none";
        }
    }
});
