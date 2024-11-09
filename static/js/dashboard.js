let efficiencyChart;

document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
});

function updateDashboard() {
    fetchEfficiencyData();
    fetchMaintenancePredictions();
    fetchOptimizationSuggestions();
    fetchRealTimeData();
}

async function fetchEfficiencyData() {
    try {
        const response = await fetch('/api/efficiency');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        updateEfficiencyChart(data);
    } catch (error) {
        console.error('Error fetching efficiency data:', error);
        displayErrorMessage('efficiency-chart', 'Failed to load efficiency data');
    }
}

function updateEfficiencyChart(data) {
    const ctx = document.getElementById('efficiency-chart').getContext('2d');
    
    if (efficiencyChart) {
        efficiencyChart.destroy();
    }
    
    efficiencyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
            datasets: [{
                label: 'Efficiency',
                data: data.map(d => d.efficiency),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    });
}

async function fetchMaintenancePredictions() {
    try {
        const response = await fetch('/api/maintenance');
        const data = await response.json();
        updateMaintenanceAlerts(data);
    } catch (error) {
        console.error('Error fetching maintenance predictions:', error);
    }
}

async function fetchOptimizationSuggestions() {
    try {
        const response = await fetch('/api/optimization');
        const data = await response.json();
        updateOptimizationSuggestions(data);
    } catch (error) {
        console.error('Error fetching optimization suggestions:', error);
    }
}

async function fetchRealTimeData() {
    try {
        const response = await fetch('/api/realtime');
        const data = await response.json();
        updateRealTimeData(data);
    } catch (error) {
        console.error('Error fetching real-time data:', error);
    }
}

function updateMaintenanceAlerts(data) {
    const alertsContainer = document.getElementById('maintenance-alerts');
    alertsContainer.innerHTML = '';

    data.forEach(item => {
        const alertElement = document.createElement('div');
        alertElement.classList.add('maintenance-item', `urgency-${item.urgency.toLowerCase()}`);
        alertElement.innerHTML = `
            <strong>${item.component}</strong><br>
            Next Maintenance: ${new Date(item.nextMaintenance).toLocaleDateString()}<br>
            Urgency: ${item.urgency}
        `;
        alertsContainer.appendChild(alertElement);
    });
}

function updateOptimizationSuggestions(data) {
    const suggestionsContainer = document.getElementById('optimization-suggestions');
    suggestionsContainer.innerHTML = '<h3>Optimization Suggestions:</h3>';
    const list = document.createElement('ul');
    data.forEach(suggestion => {
        const listItem = document.createElement('li');
        listItem.textContent = suggestion;
        list.appendChild(listItem);
    });
    suggestionsContainer.appendChild(list);
}

function updateRealTimeData(data) {
    const powerOutput = document.getElementById('power-output');
    const weatherConditions = document.getElementById('weather-conditions');

    powerOutput.innerHTML = `
        <h3>Power Output</h3>
        <p>${data.powerOutput.toFixed(2)} kW</p>
    `;

    weatherConditions.innerHTML = `
        <h3>Weather Conditions</h3>
        <p>Temperature: ${data.temperature.toFixed(1)}°C</p>
        <p>Sun Intensity: ${data.sunIntensity.toFixed(0)} W/m²</p>
        <p>Cloud Cover: ${data.cloudCover}%</p>
    `;
}

// Add event listener for window resize
window.addEventListener('resize', () => {
    if (efficiencyChart) {
        efficiencyChart.resize();
    }
});

// Update dashboard every 5 minutes
setInterval(updateDashboard, 5 * 60 * 1000);

// Initial update
updateDashboard();

document.addEventListener('DOMContentLoaded', function() {
    var sidebar = document.getElementById('sidebar');
    var sidebarCollapse = document.getElementById('sidebarCollapse');

    sidebarCollapse.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        var isClickInside = sidebar.contains(event.target) || sidebarCollapse.contains(event.target);
        if (!isClickInside && window.innerWidth <= 768) {
            sidebar.classList.add('active');
        }
    });

    // Adjust sidebar on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});
