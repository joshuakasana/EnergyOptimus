document.addEventListener('DOMContentLoaded', function () {
    const scrollLeft = document.querySelector('.scroll-left');
    const scrollRight = document.querySelector('.scroll-right');
    const scrollContainer = document.querySelector('.row');

    scrollLeft.addEventListener('click', function () {
        scrollContainer.scrollBy({
            left: -200,
            behavior: 'smooth'
        });
    });

    scrollRight.addEventListener('click', function () {
        scrollContainer.scrollBy({
            left: 200,
            behavior: 'smooth'
        });
    });
});


// Sample data for energy consumption trends
var consumptionData = {
    labels: ["January", "February", "March", "April", "May", "June"],
    datasets: [{
        label: "Energy Consumption (kWh)",
        data: [15, 20, 18, 22, 19, 21], // Sample consumption data for each month
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 2
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
var ctx = document.getElementById('energyChart').getContext('2d');

// Create the chart
var energyChart = new Chart(ctx, {
    type: 'line',
    data: consumptionData,
    options: chartOptions
});

