function updateEnergyConsumption() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                document.getElementById("average-energy-yesterday").innerText = data.average_energy_yesterday + ' kWh';
                document.getElementById("average-energy-today").innerText = data.average_energy_today + ' kWh';
            }
        }
    };
    xhr.open("GET", "/get_energy_consumption", true);
    xhr.send();
}

// Update energy consumption every 5 seconds
setInterval(updateEnergyConsumption, 5000);

// Initial update
updateEnergyConsumption();
