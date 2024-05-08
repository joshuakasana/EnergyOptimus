function updatePlots() {
    fetch('/track_energy_cost')
    .then(response => response.json())
    .then(data => {
        // Check if data is empty or missing
        if (!data.target_expense || !data.cumulative_hourly_costs) {
            console.error('Data is empty or missing.');
            return;
        }

        // Extract data
        let cumulative_hourly_costs = data.cumulative_hourly_costs.map(entry => entry[1]); // Extract costs from the tuple
        let timestamps = data.cumulative_hourly_costs.map(entry => new Date(entry[0])); // Convert timestamps to JavaScript Date objects
        let target_expense = data.target_expense;

        // Log timestamps for debugging
        // console.log('Timestamps:', timestamps);
        // console.log("Target Expense", target_expense);
        // console.log("Cummulative Expenses", cumulative_hourly_costs);

        // Create an array with the same length as timestamps, each element being the constant target_expense value
        let target_expense_values = Array(timestamps.length).fill(target_expense);

        // Plotly traces
        let consumption_costs_trace = {
            x: timestamps,
            y: cumulative_hourly_costs, // Use cumulative hourly costs instead of hourly_consumption_costs
            mode: 'lines+markers',
            name: 'Cumulative Hourly Costs' // Adjust the trace name
        };

        // Plotly traces
        let target_expense_trace = {
            x: timestamps,
            y: target_expense_values,
            mode: 'lines+markers',
            name: 'Target Expense'
        };

        let layout = {
            title: 'Cost vs Time',
            xaxis: {
                title: 'Time',
                rangeslider: { visible: false },
                // For customizing the x-axis range, adjust the range based on the timestamps
                range: [timestamps[0], timestamps[timestamps.length - 1]]
            },
            yaxis: { title: 'Consumption Costs' }, // Corrected the y-axis title
            showlegend: true
        };

        // Update or create the plot
        if (window.energyPlot) {
            // Update existing plot
            let data = [consumption_costs_trace, target_expense_trace];
            Plotly.react('cost-plot', data, layout)
        } else {
            let data = [consumption_costs_trace, target_expense_trace];
            window.energyPlot = Plotly.newPlot('cost-plot', data, layout);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call updatePlots initially and then every 5 seconds
updatePlots();
setInterval(updatePlots, 5000);
