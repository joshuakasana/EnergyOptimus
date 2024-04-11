function updatePlots() {
    fetch('/get_energy_data')
    .then(response => response.json())
    .then(data => {
        // Check if data is empty
        if (!data.timestamps || !data.energy_values || !data.predicted_energy_values) {
            console.error('Data is empty.');
            return;
        }

        // Extract data
        let timestamps = data.timestamps;
        let energy_values = data.energy_values;
        let predicted_energy_values = data.predicted_energy_values;

        // Plotly traces
        let energy_trace = {
            x: timestamps,
            y: energy_values,
            mode: 'lines+markers',
            name: 'Actual Energy'
        };

        let predicted_energy_trace = {
            x: timestamps,
            y: predicted_energy_values,
            mode: 'lines+markers',
            name: 'Predicted Energy'
        };

        let layout = {
            title: 'Energy Consumption vs Time',
            xaxis: {
                title: 'Time',
                rangeslider: { visible: false },
                range: [Math.max(0, timestamps.length - 19), Math.max(40, timestamps.length)]
            },
            yaxis: { title: 'Energy Consumption' },
            showlegend: true
        };

        // Update or create the plot
        if (window.energyPlot) {
            // Update existing plot
            let data = [energy_trace, predicted_energy_trace];
            Plotly.react('energy-trace', data, layout)
        } else {
            let data = [energy_trace, predicted_energy_trace];
            window.energyPlot = Plotly.newPlot('energy-plot', data, layout);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call updatePlots initially and then every 5 seconds
updatePlots();
setInterval(updatePlots, 5000);
