let charts = {};
let latestProduction = 0;
let latestConsumption = 0;

document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    setupSidebarToggle();
    // Update every 5 seconds
    setInterval(updateDashboard, 5000);
    updateDeviceList();
    fetchCurrentWeather();
    updateWeatherForecast();

    const alertToggle = document.getElementById('alertToggle');
    const notificationArea = document.getElementById('notification-area');

    alertToggle.addEventListener('click', function() {
        notificationArea.classList.toggle('hidden');
        updateAlertToggleIcon();
    });

    function updateAlertToggleIcon() {
        alertToggle.textContent = notificationArea.classList.contains('hidden') ? '🔔' : '🔕';
    }

    fetchSystemStatus();
});

function updateDashboard() {
    fetchEnergyProduction();
    fetchWeatherForecast();
    fetchEnergyConsumption();
    fetchSolarPerformance();
    fetchMaintenancePredictions();
}

async function fetchEnergyProduction() {
    await fetchChartData('energyProductionChart', 'Energy Production', '/api/energy_production');
    checkEnergyLevels(latestProduction, latestConsumption);
}

async function fetchEnergyConsumption() {
    await fetchChartData('energyConsumptionChart', 'Energy Consumption', '/api/energy_consumption');
    checkEnergyLevels(latestProduction, latestConsumption);
}

async function fetchSolarPerformance() {
    await fetchChartData('solarPerformanceChart', 'Solar Performance', '/api/solar_performance');
}

async function fetchChartData(chartId, label, url) {
    showLoading(chartId);
    try {
        const response = await fetch(url);
        const data = await response.json();
        createOrUpdateChart(chartId, label, data);
    } catch (error) {
        console.error(`Error fetching ${label} data:`, error);
        displayError(`Failed to load ${label} data`);
    } finally {
        hideLoading(chartId);
    }
}

async function fetchWeatherForecast() {
    showLoading('weatherForecast');
    try {
        const response = await fetch('/api/weather_forecast');
        const data = await response.json();
        updateWeatherForecast(data);
        checkWeatherStatus(data);
    } catch (error) {
        console.error('Error fetching weather forecast:', error);
        displayError("Failed to load weather forecast");
    } finally {
        hideLoading('weatherForecast');
    }
}

async function fetchMaintenancePredictions() {
    showLoading('maintenancePredictions');
    try {
        const response = await fetch('/api/maintenance_predictions');
        const data = await response.json();
        updateMaintenancePredictions(data);
    } catch (error) {
        console.error('Error fetching maintenance predictions:', error);
        displayError("Failed to load maintenance predictions");
    } finally {
        hideLoading('maintenancePredictions');
    }
}

function createOrUpdateChart(chartId, label, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    const chartConfig = {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: label,
                data: data.values,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 6,
                        maxRotation: 0,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 6
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    if (charts[chartId]) {
        charts[chartId].data.labels = data.labels;
        charts[chartId].data.datasets[0].data = data.values;
        charts[chartId].update();
    } else {
        charts[chartId] = new Chart(ctx, chartConfig);
    }

    if (label === 'Energy Production') {
        latestProduction = data.values[data.values.length - 1];
    } else if (label === 'Energy Consumption') {
        latestConsumption = data.values[data.values.length - 1];
    }
}

function updateWeatherForecast(data) {
    fetch('/api/weather_forecast')
        .then(response => response.json())
        .then(data => {
            const forecastContainer = document.getElementById('weatherForecast');
            forecastContainer.innerHTML = data.map(day => `
                <div class="forecast-card">
                    <p class="date">${day.date}</p>
                    <p class="icon">${day.icon}</p>
                    <p class="temperature">${day.temperature}°C</p>
                    <p class="condition">${day.condition}</p>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching weather forecast:', error);
            document.getElementById('weatherForecast').innerHTML = '<p>Failed to load weather forecast.</p>';
        });
}

function updateMaintenancePredictions(data) {
    const predictionsDiv = document.getElementById('maintenancePredictions');
    predictionsDiv.innerHTML = '';
    data.forEach(prediction => {
        const predictionElement = document.createElement('div');
        predictionElement.innerHTML = `
            <p><strong>${prediction.component}</strong>: Next maintenance on ${prediction.date}</p>
        `;
        predictionsDiv.appendChild(predictionElement);
    });
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.closest('.dashboard-item').classList.add('loading');
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    element.closest('.dashboard-item').classList.remove('loading');
}

function displayError(message) {
    const errorContainer = document.getElementById('error-container');
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger';
    errorElement.textContent = message;
    errorContainer.appendChild(errorElement);
    setTimeout(() => errorElement.remove(), 5000); // Remove after 5 seconds
}

function setupSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapse = document.getElementById('sidebarCollapse');

    sidebarCollapse.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const isClickInside = sidebar.contains(event.target) || sidebarCollapse.contains(event.target);
        if (!isClickInside && window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    });

    // Adjust sidebar on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
}

function checkEnergyLevels(production, consumption) {
    const ratio = production / consumption;
    if (ratio < 0.5) {
        addNotification("Energy consumption is significantly higher than production.", "danger");
    } else if (ratio < 0.8) {
        addNotification("Energy consumption is higher than production.", "warning");
    } else if (ratio > 1.2) {
        addNotification("Energy production is exceeding consumption.", "success");
    }
}

function checkWeatherStatus(weatherData) {
    const currentWeather = weatherData[0]; // The first item is the current weather
    if (currentWeather.condition.toLowerCase().includes("rain")) {
        addNotification("Rainy weather in Lusaka may affect solar panel efficiency today.", "warning");
    } else if (currentWeather.condition.toLowerCase().includes("cloud")) {
        addNotification("Cloudy weather in Lusaka may slightly reduce solar panel efficiency today.", "info");
    } else if (currentWeather.condition.toLowerCase().includes("clear")) {
        addNotification("Clear weather in Lusaka is ideal for solar energy production today!", "success");
    }

    // Check for extreme temperatures
    if (currentWeather.temperature > 35) {
        addNotification("High temperatures in Lusaka may affect solar panel efficiency. Ensure proper cooling.", "warning");
    } else if (currentWeather.temperature < 5) {
        addNotification("Low temperatures in Lusaka may reduce solar panel output slightly.", "info");
    }
}

function addNotification(message, type = "info") {
    const notificationArea = document.getElementById("notification-area");
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notificationArea.appendChild(notification);

    // Remove the notification after 10 seconds
    setTimeout(() => {
        notification.style.opacity = "0";
        setTimeout(() => {
            notificationArea.removeChild(notification);
        }, 300);
    }, 10000);
}

function updateDeviceList() {
    fetch('/api/devices')
    .then(response => response.json())
    .then(devices => {
        const deviceListElement = document.getElementById('deviceList');
        deviceListElement.innerHTML = '<h3>Connected Devices</h3>';
        devices.forEach(device => {
            const deviceElement = document.createElement('div');
            deviceElement.className = 'device-item';
            deviceElement.innerHTML = `
                <p><strong>${device.name}</strong> (${device.type})</p>
                <p>Location: ${device.location}</p>
                <button onclick="downloadCSV('${device.name}')">Download Data</button>
            `;
            deviceListElement.appendChild(deviceElement);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('deviceList').innerHTML = '<p>Failed to load devices.</p>';
    });
}

function downloadCSV(deviceName) {
    window.location.href = `/api/download_csv/${deviceName}`;
}

// Add this function to fetch and display current weather
function fetchCurrentWeather() {
    fetch('/api/current_weather')
        .then(response => response.json())
        .then(data => {
            const weatherDisplay = document.getElementById('currentWeather');
            weatherDisplay.innerHTML = `
                <div class="weather-icon">
                    <span class="weather-emoji">${data.icon}</span>
                </div>
                <div class="weather-info">
                    <p class="temperature">${data.temperature}°C</p>
                    <p class="condition">${data.condition}</p>
                    <p class="humidity">Humidity: ${data.humidity}%</p>
                    <p class="wind">Wind: ${data.wind_speed} km/h ${data.wind_direction}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error fetching current weather:', error);
            document.getElementById('currentWeather').innerHTML = '<p>Failed to load current weather data.</p>';
        });
}

// Add these functions to your existing dashboard.js file

const alertToggle = document.getElementById('alertToggle');
const notificationArea = document.getElementById('notification-area');

alertToggle.addEventListener('click', function() {
    notificationArea.classList.toggle('hidden');
    updateAlertToggleIcon();
});

function updateAlertToggleIcon() {
    alertToggle.textContent = notificationArea.classList.contains('hidden') ? '🔔' : '🔕';
}

// Function to add a new alert
function addAlert(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.textContent = message;

    const closeButton = document.createElement('button');
    closeButton.className = 'close-alert';
    closeButton.textContent = '×';
    closeButton.onclick = function() {
        notificationArea.removeChild(alertElement);
    };

    alertElement.appendChild(closeButton);
    notificationArea.appendChild(alertElement);

    // Show the notification area if it's hidden
    if (notificationArea.classList.contains('hidden')) {
        notificationArea.classList.remove('hidden');
        updateAlertToggleIcon();
    }
}

// Example usage:
// addAlert('Energy production is above average today!', 'success');
// addAlert('Battery levels are low. Consider reducing consumption.', 'warning');

function fetchSystemStatus() {
    fetch('/api/system_status')
        .then(response => response.json())
        .then(data => {
            const systemStatusDiv = document.getElementById('systemStatus');
            systemStatusDiv.innerHTML = `
                <p>Total Production: ${data.total_production} kWh</p>
                <p>Average Battery Level: ${data.average_battery}%</p>
                <p>Overall Status: ${data.overall_status}</p>
            `;
        })
        .catch(error => console.error('Error fetching system status:', error));
}
