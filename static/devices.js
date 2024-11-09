document.addEventListener('DOMContentLoaded', function() {
    const deviceForm = document.getElementById('deviceForm');
    const deviceList = document.getElementById('deviceList');

    deviceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const deviceName = document.getElementById('deviceName').value;
        const deviceType = document.getElementById('deviceType').value;
        const deviceLocation = document.getElementById('deviceLocation').value;

        fetch('/api/connect_device', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: deviceName, type: deviceType, location: deviceLocation }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Device connected successfully!', 'success');
                deviceForm.reset();
                fetchDevices();
            } else {
                showAlert('Failed to connect device. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred. Please try again.', 'error');
        });
    });

    fetchDevices();
});

function fetchDevices() {
    fetch('/api/devices')
    .then(response => response.json())
    .then(devices => {
        deviceList.innerHTML = '<h3>Connected Devices</h3>';
        devices.forEach(device => {
            const deviceElement = document.createElement('div');
            deviceElement.className = 'device-item';
            deviceElement.innerHTML = `
                <p><strong>${device.name}</strong> (${device.type})</p>
                <p>Location: ${device.location}</p>
                <p>IP: ${device.ip}, Port: ${device.port}</p>
                <p>Protocol: ${device.protocol}</p>
                <p>Status: ${device.status}</p>
                <button onclick="disconnectDevice('${device.name}')">Disconnect</button>
            `;
            deviceList.appendChild(deviceElement);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
        deviceList.innerHTML = '<p>Failed to load devices.</p>';
    });
}

function disconnectDevice(deviceName) {
    fetch('/api/disconnect_device', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: deviceName }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Device disconnected successfully!');
            updateDeviceList();
        } else {
            alert('Failed to disconnect device: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}
