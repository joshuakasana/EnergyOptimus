document.addEventListener('DOMContentLoaded', function() {
    var currentDateTimeElement = document.getElementById('currentDate');
    
    function updateDateTime() {
        var currentDate = new Date();

        var optionsDate = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        var formattedDate = currentDate.toLocaleDateString('en-US', optionsDate);

        var optionsTime = { hour: 'numeric', minute: 'numeric', second: 'numeric' };
        var formattedTime = currentDate.toLocaleTimeString('en-US', optionsTime);

        // currentDateTimeElement.textContent = 'Today is: ' + formattedDate + ', ' + formattedTime;
        currentDateTimeElement.textContent = formattedDate + ', ' + formattedTime;
    }

    // Call updateDateTime function immediately to display initial time
    updateDateTime();

    // Update time every second
    setInterval(updateDateTime, 1000);
});
