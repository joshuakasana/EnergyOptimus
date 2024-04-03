function updateCurrentData() {
    // Make a GET request to the Flask route to fetch current data
    fetch('/get_current_data')
    .then(response => response.json())
    .then(data => {
        // Update the webpage with the fetched data
        document.getElementById('current-humidity').textContent = data.humidity + '%';
        document.getElementById('current-temperature').textContent = data.temperature + '°C';
        
        // Update the styles based on humidity
        let humidityCard = document.getElementById('humidity-card');
        humidityCard.classList.remove('bg-danger', 'bg-success', 'bg-info'); // Clear existing classes
        if (data.humidity < 30) {
            humidityCard.classList.add('bg-danger');
        } else if (data.humidity >= 40 && data.humidity <= 60) {
            humidityCard.classList.add('bg-success');
        } else if (data.humidity >= 61 && data.humidity <= 74) {
            humidityCard.classList.add('bg-info');
        } else {
            humidityCard.classList.add('bg-primary');
        }

        // Update the styles based on temperature
        let temperatureCard = document.getElementById('temperature-card');
        temperatureCard.classList.remove('bg-primary', 'bg-info', 'bg-success', 'bg-warning', 'bg-danger'); // Clear existing classes
        if (data.temperature < 13) {
            temperatureCard.classList.add('bg-primary');
        } else if (data.temperature >= 13 && data.temperature <= 18) {
            temperatureCard.classList.add('bg-info');
        } else if (data.temperature >= 19 && data.temperature <= 22) {
            temperatureCard.classList.add('bg-success');
        } else if (data.temperature >= 23 && data.temperature <= 29) {
            temperatureCard.classList.add('bg-warning');
        } else {
            temperatureCard.classList.add('bg-danger');
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call updateCurrentData initially and then every 5 seconds
updateCurrentData();
setInterval(updateCurrentData, 5000);