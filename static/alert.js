document.addEventListener('DOMContentLoaded', function() {
    const alertBar = document.getElementById('alertBar');
    const alertMessage = document.getElementById('alertMessage');
    const alertClose = document.getElementById('alertClose');
    
    // Add a new toggle button
    const alertToggle = document.createElement('button');
    alertToggle.id = 'alertToggle';
    alertToggle.className = 'alert-toggle';
    alertToggle.textContent = '▲';
    alertBar.appendChild(alertToggle);

    // Existing show alert function
    window.showAlert = function(message, type = 'error') {
        alertMessage.textContent = message;
        alertBar.className = 'alert-bar show';
        
        if (type === 'success') {
            alertBar.style.backgroundColor = '#d4edda';
            alertBar.style.color = '#155724';
        } else if (type === 'warning') {
            alertBar.style.backgroundColor = '#fff3cd';
            alertBar.style.color = '#856404';
        } else {
            alertBar.style.backgroundColor = '#f8d7da';
            alertBar.style.color = '#721c24';
        }
    };

    // Modified hide alert function
    window.hideAlert = function() {
        alertBar.classList.add('retracted');
    };

    // New function to toggle the alert bar
    function toggleAlertBar() {
        alertBar.classList.toggle('retracted');
        alertToggle.textContent = alertBar.classList.contains('retracted') ? '▼' : '▲';
    }

    // Close button functionality (you can keep or remove this)
    alertClose.addEventListener('click', hideAlert);

    // Toggle button functionality
    alertToggle.addEventListener('click', toggleAlertBar);

    // Auto-hide after 5 seconds (you can keep or remove this)
    window.autoHideAlert = function() {
        setTimeout(hideAlert, 5000);
    };
});
