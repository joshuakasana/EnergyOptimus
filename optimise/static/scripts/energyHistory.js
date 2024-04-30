// Sample data for energy consumption history
var consumptionData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
    datasets: [{
        label: "Energy Consumption (kWh)",
        data: [150, 200, 180, 220, 190, 210, 250], // Sample consumption data for each month
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 2,
        pointRadius: 5,
        pointBackgroundColor: "rgba(54, 162, 235, 1)",
        pointBorderColor: "#fff",
        pointHoverRadius: 8,
        pointHoverBackgroundColor: "rgba(54, 162, 235, 1)",
        pointHoverBorderColor: "#fff"
    },
    {
        label: "Constant Value",
        data: Array(7).fill(240), // Replace 300 with the constant value you want to plot
        borderColor: "rgba(255, 99, 132, 1)", // Red color for the line
        borderWidth: 2,
        fill: false, // Don't fill the area under the line
        pointRadius: 0 // Don't display points on the line
    }
]
};

// Configure options for the chart
var chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
};

// Get the canvas element
var ctx = document.getElementById('consumptionChart').getContext('2d');

// Create the chart
var consumptionChart = new Chart(ctx, {
    type: 'line',
    data: consumptionData,
    options: chartOptions
});
