document.addEventListener('DOMContentLoaded', function() {
    // Profile Form Handler
    const profileForm = document.getElementById('profileForm');
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value
        };
        
        try {
            const response = await fetch('/api/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                showNotification('Profile updated successfully', 'success');
            } else {
                showNotification('Failed to update profile', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to update profile', 'error');
        }
    });

    // Notification Preferences Form Handler
    const notificationForm = document.getElementById('notificationForm');
    notificationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const notificationMethods = Array.from(document.querySelectorAll('input[name="notification_method"]:checked'))
            .map(input => input.value);
        
        const alertTypes = Array.from(document.querySelectorAll('input[name="alert_type"]:checked'))
            .map(input => input.value);
        
        const formData = {
            notification_methods: notificationMethods,
            alert_types: alertTypes
        };
        
        try {
            const response = await fetch('/api/update_notification_preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                showNotification('Notification preferences updated successfully', 'success');
            } else {
                showNotification('Failed to update notification preferences', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to update notification preferences', 'error');
        }
    });

    // System Preferences Form Handler
    const systemPreferencesForm = document.getElementById('systemPreferencesForm');
    systemPreferencesForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            timezone: document.getElementById('timezone').value,
            updateFrequency: document.getElementById('updateFrequency').value
        };
        
        try {
            const response = await fetch('/api/update_system_preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                showNotification('System preferences updated successfully', 'success');
            } else {
                showNotification('Failed to update system preferences', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to update system preferences', 'error');
        }
    });
});

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
