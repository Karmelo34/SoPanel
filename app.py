from random import random
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, current_app, send_file
from datetime import datetime, timedelta
import socketio
from weather_api import fetch_current_weather, fetch_forecast_data, fetch_historical_weather_data
from pv_simulator import PVSimulator
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import socket
import json
import threading
import time
from contextlib import closing
from flask_socketio import SocketIO, emit
import shutil
import os
import csv

from flask_wtf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///solar_data.db'
app.config["SECRET_KEY"] = '123456789'  
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

pv_system = PVSimulator()
LOCATION = "Lusaka"
DISCOVERY_PORT_RANGE = range(5001, 5011)  # Define a range of ports to try

class SolarData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    energy_production = db.Column(db.Float, nullable=False)
    solar_irradiance = db.Column(db.Float, nullable=False)
    panel_temperature = db.Column(db.Float, nullable=False)
    ambient_temperature = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, nullable=False)
    weather_condition = db.Column(db.String(50), nullable=False)
    system_status = db.Column(db.String(20), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    device = db.relationship('Device', backref=db.backref('solar_data', lazy=True))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    





class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('devices', lazy=True))

@app.route('/')
def index():
    return render_template('dashboard.html')

def generate_mock_data():
    now = datetime.now()
    labels = [(now - timedelta(minutes=i)).strftime('%H:%M') for i in range(60, 0, -1)]
    
    return {
        'labels': labels,
        'values': [random.uniform(0, 100) for _ in range(60)]  # Ensure values are within a reasonable range
    }

@app.route('/api/energy_production')
def energy_production():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    historical_data = fetch_historical_weather_data(LOCATION, start_date, end_date)
    current_weather = fetch_current_weather(LOCATION)
    
    user_devices = Device.query.filter_by(user_id=1).all()
    
    hourly_data = []
    for device in user_devices:
        if device.type == 'simulator':
            simulator = PVSimulator()  # Create a new simulator instance for each device
            for day in historical_data:
                hourly_data.append({
                    "timestamp": day['date'],
                    "production": simulator.simulate_production({
                        'temperature': day['max_temp'],
                        'cloud': day['cloud'],
                        'condition': 'Clear'  # Assuming clear weather for historical data
                    }),
                    "device_name": device.name
                })
            
            # Add current hour
            hourly_data.append({
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "production": simulator.simulate_production(current_weather),
                "device_name": device.name
            })
        elif device.type == 'real_device':
            # Here you would fetch real data from the device
            # For now, we'll just add dummy data
            hourly_data.append({
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "production": random.uniform(0, 100),
                "device_name": device.name
            })
    
    return jsonify({
        "labels": [item["timestamp"] for item in hourly_data],
        "values": [item["production"] for item in hourly_data],
        "devices": [item["device_name"] for item in hourly_data]
    })

@app.route('/api/energy_consumption')
def energy_consumption():
    # For simplicity, we'll generate random consumption data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    hourly_data = []
    current_date = start_date
    while current_date <= end_date:
        hourly_data.append({
            "timestamp": current_date.strftime('%Y-%m-%d %H:%M:%S'),
            "consumption": pv_system.simulate_consumption()
        })
        current_date += timedelta(hours=1)
    
    return jsonify({
        "labels": [item["timestamp"] for item in hourly_data],
        "values": [item["consumption"] for item in hourly_data]
    })

@app.route('/api/solar_performance')
def solar_performance():
    current_weather = fetch_current_weather(LOCATION)
    return jsonify({
        "current_output": pv_system.simulate_production(current_weather),
        "system_health": pv_system.get_system_health()
    })

@app.route('/api/maintenance_predictions')
def maintenance_predictions():
    return jsonify([
        {
            "component": "Solar Panels",
            "date": pv_system.get_maintenance_prediction()
        },
        {
            "component": "Inverter",
            "date": pv_system.get_maintenance_prediction()
        }
    ])

@app.route('/api/weather_forecast')
def weather_forecast():
    current_weather = fetch_current_weather(LOCATION)
    forecast = fetch_forecast_data(LOCATION, days=5)
    
    formatted_forecast = [{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'icon': get_weather_icon(current_weather['condition']),
        'temperature': current_weather['temperature'],
        'condition': current_weather['condition']
    }]
    
    for day in forecast:
        formatted_forecast.append({
            'date': day['date'],
            'icon': get_weather_icon(day['condition']),
            'temperature': day['max_temp'],
            'condition': day['condition']
        })
    
    return jsonify(formatted_forecast)

@app.route('/api/current_weather')
def current_weather():
    weather_data = fetch_current_weather(LOCATION)
    return jsonify({
        'temperature': weather_data['temperature'],
        'condition': weather_data['condition'],
        'humidity': weather_data['humidity'],
        'wind_speed': weather_data['wind_speed'],
        'wind_direction': weather_data['wind_direction'],
        'icon': get_weather_icon(weather_data['condition'])
    })

def get_weather_icon(condition):
    condition = condition.lower()
    if 'clear' in condition or 'sunny' in condition:
        return '☀️'
    elif 'partly cloudy' in condition:
        return '⛅'
    elif 'cloudy' in condition or 'overcast' in condition:
        return '☁️'
    elif 'rain' in condition:
        return '🌧️'
    elif 'snow' in condition:
        return '❄️'
    elif 'storm' in condition or 'thunder' in condition:
        return '⛈️'
    else:
        return '🌤️'  # Default to partly sunny


@app.route('/historical_data')
def historical_data():
    start_date = request.args.get('start_date', default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get('end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the end date
    
    data = SolarData.query.filter(
        SolarData.timestamp.between(start_date, end_date)
    ).order_by(SolarData.timestamp.desc()).all()
    
    return render_template('historical_data.html', 
                         data=data, 
                         start_date=start_date.strftime('%Y-%m-%d'), 
                         end_date=(end_date - timedelta(days=1)).strftime('%Y-%m-%d'))

@app.route('/api/historical_data')
def api_historical_data():
    start_date = request.args.get('start_date', default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get('end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    user_devices = Device.query.filter_by(user_id=1).all()
    device_ids = [device.id for device in user_devices]
    
    data = SolarData.query.filter(
        SolarData.timestamp.between(start_date, end_date),
        SolarData.device_id.in_(device_ids)
    ).order_by(SolarData.timestamp.desc()).all()
    
    return jsonify([{
        'timestamp': entry.timestamp,
        'energy_production': entry.energy_production,
        'solar_irradiance': entry.solar_irradiance,
        'panel_temperature': entry.panel_temperature,
        'ambient_temperature': entry.ambient_temperature,
        'efficiency': entry.efficiency,
        'weather_condition': entry.weather_condition,
        'system_status': entry.system_status,
        'device_name': entry.device.name
    } for entry in data])

# Add this function to populate the database with some initial data
def populate_db():
    # Check if the default user already exists
    default_user = User.query.filter_by(username="default_user").first()
    if not default_user:
        # Create a default user only if it doesn't exist
        default_user = User(username="default_user", password="default_password")
        db.session.add(default_user)
        db.session.commit()
    
    # Check if the default device already exists
    default_device = Device.query.filter_by(name="Default Device", user_id=default_user.id).first()
    if not default_device:
        # Create a default device only if it doesn't exist
        default_device = Device(
            device_id="DEFAULT_001",  # Add a default device_id
            name="Default Device",
            type="simulator",  # Add a default type
            ip="127.0.0.1",  # Add a default IP
            port=5000,  # Add a default port
            user_id=default_user.id
        )
        db.session.add(default_device)
        db.session.commit()
    
    if SolarData.query.first() is None:
        # Use historical data from your dashboard
        historical_data = [
            {
                "timestamp": "2024-10-25 10:00:00",
                "energy_production": 45.2,
                "solar_irradiance": 750.5,
                "panel_temperature": 35.6,
                "ambient_temperature": 28.3,
                "efficiency": 22.1,
                "weather_condition": "Sunny",
                "system_status": "Normal"
            },
            # ... other entries ...
        ]

        for entry_data in historical_data:
            entry = SolarData(
                timestamp=datetime.strptime(entry_data["timestamp"], "%Y-%m-%d %H:%M:%S"),
                energy_production=entry_data["energy_production"],

                solar_irradiance=entry_data["solar_irradiance"],
                panel_temperature=entry_data["panel_temperature"],

                ambient_temperature=entry_data["ambient_temperature"],
                efficiency=entry_data["efficiency"],

                weather_condition=entry_data["weather_condition"],
                system_status=entry_data["system_status"],
                device_id=default_device.id  # Add this line
            )
            db.session.add(entry)

        db.session.commit()



def connect_to_device(device):
    """Connect to device and start data collection"""
    try:
        device.is_connected = True
        db.session.commit()
        
        while device.is_connected:
            # Collect data from device
            data = collect_log_data(device) # type: ignore
            if data:
                # Store data in database
                store_log_data(device, data) # type: ignore
                # Broadcast to connected clients
                broadcast_device_data(device.id, data)
            
            time.sleep(5)  # Update interval
            
    except Exception as e:
        print(f"Error connecting to device {device.id}: {e}")
        device.is_connected = False
        db.session.commit()

@app.route('/connect_devices', methods=['GET', 'POST'])
def connect_devices():
    if request.method == 'POST':
        device_id = request.form.get('device_id')
        device = Device.query.filter_by(device_id=device_id).first()
        
        if device:
            device.user_id = 1
            db.session.commit()
            threading.Thread(target=connect_to_device, args=(device,), daemon=True).start()
            flash(f'Device {device.name} connected successfully!', 'success')
        else:
            flash('Device not found', 'error')
        
        return redirect(url_for('connect_devices'))
    

    # GET request: display the form and list of available devices
    available_devices = Device.query.filter_by(user_id=1).all()  # Devices not yet assigned to a user
    user_devices = Device.query.filter_by(user_id=1).all()
    return render_template('connect_devices.html', available_devices=available_devices, user_devices=user_devices)

@login_manager.user_loader
def load_user(user_id):
    
    return User.query.get(int(user_id))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(username=request.form.get("username"),
                    password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please log in.', 'success')

        return redirect(url_for("login"))
    

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for("dashboard"))
        else:
            flash('Invalid username or password.', 'error')
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route('/dashboard')

@login_required
def dashboard():
    return render_template('dashboard.html')



# Make sure to create the database tables and populate initial data
if __name__ == '__main__':
    with app.app_context():
        
        db.create_all()

        populate_db()



    

    app.run(debug=True, port=5000)

@app.route('/api/submit_data', methods=['POST'])
def submit_data():
    data = request.json
    device_id = data.get('device_id')
    device = Device.query.get(device_id)
    
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    new_data = SolarData(
        timestamp=datetime.now(),
        energy_production=data.get('energy_production'),
        solar_irradiance=data.get('solar_irradiance'),
        panel_temperature=data.get('panel_temperature'),
        ambient_temperature=data.get('ambient_temperature'),
        efficiency=data.get('efficiency'),
        weather_condition=data.get('weather_condition'),
        system_status=data.get('system_status'),
        device_id=device_id
    )
    
    db.session.add(new_data)
    db.session.commit()
    
    return jsonify({'message': 'Data submitted successfully'}), 200

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    try:
        current_user.notification_email = data.get('email')
        current_user.notification_phone = data.get('phone')
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/update_notification_preferences', methods=['POST'])
@login_required
def update_notification_preferences():
    data = request.json
    try:
        current_user.notification_preferences = data.get('notification_methods', [])
        current_user.alert_preferences = data.get('alert_types', [])
        db.session.commit()
        return jsonify({'message': 'Preferences updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/update_system_preferences', methods=['POST'])
@login_required
def update_system_preferences():
    data = request.json
    try:
        current_user.timezone = data.get('timezone')
        current_user.update_frequency = data.get('updateFrequency')
        db.session.commit()
        return jsonify({'message': 'System preferences updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/devices')
@login_required
def get_devices():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': device.id,
        'name': device.name,
        'type': device.type,
        'ip': device.ip,
        'protocol': device.protocol,
        'status': 'online' if device.is_connected else 'offline'
    } for device in devices])

@app.route('/api/devices/add', methods=['POST'])
@login_required
def add_device():
    try:
        device = Device(
            name=f"{request.form['deviceType']}_{request.form['ip']}",
            type=request.form['deviceType'],
            ip=request.form['ip'],
            port=int(request.form['port']),
            protocol=request.form['protocol'],
            user_id=current_user.id
        )
        db.session.add(device)
        db.session.commit()
        
        # Start device connection in background
        threading.Thread(
            target=connect_to_device,
            args=(device,),
            daemon=True
        ).start()
        
        return jsonify({
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'ip': device.ip,
            'protocol': device.protocol
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/devices/<int:device_id>/disconnect', methods=['POST'])
@login_required
def disconnect_device(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Implement device disconnection logic here
        device.is_connected = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False
    
    # Send initial device statuses
    devices = Device.query.filter_by(user_id=current_user.id).all()
    for device in devices:
        emit('device_status', {
            'device_id': device.id,
            'status': 'online' if device.is_connected else 'offline'
        })

def broadcast_device_data(device_id, data):
    """Broadcast device data to connected clients"""
    socketio.emit('device_data', {
        'device_id': device_id,
        'energy_production': data.get('energy_production'),
        'efficiency': data.get('efficiency'),
        'status': 'online'
    })

@app.route('/device-connections')
@login_required
def device_connections():
    return render_template('device_connections.html')

@app.route('/export-database')
@login_required
def export_database():
    success, result = export_database_to_csv()
    
    if success:
        # Create a zip file of the export directory
        export_dir = result
        shutil.make_archive(export_dir, 'zip', export_dir)
        
        # Send the zip file
        return send_file(
            f'{export_dir}.zip',
            mimetype='application/zip',
            as_attachment=True,
            download_name='database_export.zip'
        )
    else:
        flash(f'Export failed: {result}', 'error')
        return redirect(url_for('settings'))

def export_database_to_csv():
    try:
        export_dir = 'database_export'
        os.makedirs(export_dir, exist_ok=True)
        
        # Export each table to a CSV file
        for table in db.Model.__subclasses__():
            data = table.query.all()
            if not data:
                continue
                
            filename = f"{export_dir}/{table.__tablename__}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write headers
                writer.writerow([column.name for column in table.__table__.columns])
                # Write data
                for record in data:
                    writer.writerow([getattr(record, column.name) for column in table.__table__.columns])
        
        return True, export_dir
    except Exception as e:
        return False, str(e)

@app.route('/some-action')
def some_action():
    # Success notification
    flash('Operation completed successfully!', 'success')
    
    # Error notification
    flash('An error occurred!', 'error')
    
    # Warning notification
    flash('Please check your settings.', 'warning')
    
    # Info notification
    flash('System update available.', 'info')
    
    return redirect(url_for('dashboard'))

def collect_sensor_data():
    """
    Function to collect real-time sensor data and store it in the database
    This could be called by a scheduler or run in a separate process
    """
    new_data = historical_data(
        energy_production=get_energy_production(),  # Your sensor reading function
        solar_irradiance=get_solar_irradiance(),   # Your sensor reading function
        panel_temperature=get_panel_temperature(),  # Your sensor reading function
        ambient_temperature=get_ambient_temp(),     # Your sensor reading function
        
        weather_condition=get_weather_condition(),  # Your weather API function
        system_status=get_system_status()          # Your status check function
    )
    
    db.session.add(new_data)
    db.session.commit()

def get_weather_condition():
    weather_data = fetch_current_weather(LOCATION)
    return weather_data['condition']

# Set up a scheduler to collect data periodically
scheduler = BackgroundScheduler()
scheduler.add_job(func=collect_sensor_data, trigger="interval", minutes=5)
scheduler.start()

def get_energy_production():
    """Get energy production from PV system"""
    return pv_system.simulate_production(fetch_current_weather(LOCATION))

def get_solar_irradiance():
    """Get solar irradiance from weather data"""
    weather_data = fetch_current_weather(LOCATION)
    return weather_data.get('solar_irradiance', 0)  # Default to 0 if not available

def get_panel_temperature():
    """Get panel temperature from sensors"""
    ambient_temp = get_ambient_temp()
    # Panel temp is typically 20-30°C above ambient in full sun
    return ambient_temp + 25

def get_ambient_temp():
    """Get ambient temperature from weather API"""
    weather_data = fetch_current_weather(LOCATION)
    return weather_data['temperature']

def get_system_status():
    """Get current system operational status"""
    return "Normal"  # Replace with actual system status logic

@app.route('/api/historical_data')
def get_historical_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Query your database for the data
    historical_data = historical_data.query.filter(
        historical_data.timestamp.between(start_date, end_date)
    ).order_by(historical_data.timestamp.desc()).all()
    
    # Convert the data to a list of dictionaries
    data = [{
        'timestamp': entry.timestamp.isoformat(),
        'energy_production': entry.energy_production,
        'solar_irradiance': entry.solar_irradiance,
        'panel_temperature': entry.panel_temperature,
        'ambient_temperature': entry.ambient_temperature,
        'efficiency': entry.efficiency,
        'weather_condition': entry.weather_condition,
        'system_status': entry.system_status
    } for entry in historical_data]
    
    return jsonify(data)
