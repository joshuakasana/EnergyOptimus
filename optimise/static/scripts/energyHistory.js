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
    }]
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
