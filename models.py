from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __bind_key__ = 'users'  # This line specifies to use the 'users' database
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
    name = db.Column(db.String(1000))
    notification_preferences = db.Column(db.JSON, default=list)
    alert_preferences = db.Column(db.JSON, default=list)
    timezone = db.Column(db.String(50), default='UTC')
    update_frequency = db.Column(db.Integer, default=5)  # in minutes

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    solar_data = db.relationship('SolarData', backref='device', lazy='dynamic')

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

class HistoricalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    energy_production = db.Column(db.Float)
    solar_irradiance = db.Column(db.Float)
    panel_temperature = db.Column(db.Float)
    ambient_temperature = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    weather_condition = db.Column(db.String(50))
    system_status = db.Column(db.String(50))

    def __repr__(self):
        return f'<HistoricalData {self.timestamp}>'

# Add any other fields or methods as needed
