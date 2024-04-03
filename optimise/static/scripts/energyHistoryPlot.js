// Function to fetch data from the server and update the plot
function updatePlots() {
    fetch('/get_energy_data')
    .then(response => response.json())
    .then(data => {
        // Extract data
        let timestamps = data.timestamps;
        let energy_values = data.energy_values;
        let predicted_energy_values = data.predicted_energy_values;

        // Plotly traces
        let energy_trace = {
            x: timestamps,
            y: energy_values,
            mode: 'lines+markers',
            name: 'Energy'
        };

        let predicted_energy_trace = {
            x: timestamps,
            y: predicted_energy_values,
            mode: 'lines+markers',
            name: 'Predicted Energy'
        };

        // Update or create the plot
        if (window.energyPlot) {
            // Update existing plot
            Plotly.restyle('energy-plot', energy_trace, 0);
            Plotly.restyle('energy-plot', predicted_energy_trace, 1);
        } else {
            // Create new plot
            let layout = {
                title: 'Energy Consumption vs Time',
                xaxis: {title: 'Time'},
                yaxis: {title: 'Energy Consumption'},
                showlegend: true
            };

            let data = [energy_trace, predicted_energy_trace];
            window.energyPlot = Plotly.newPlot('energy-plot', data, layout);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call updatePlots initially and then every 5 seconds
updatePlots();
setInterval(updatePlots, 5000);