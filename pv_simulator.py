import random
from datetime import datetime, timedelta
from datasource import DataSource

class PVSimulator(DataSource):
    def __init__(self, num_panels=20, panel_capacity=300, inverter_efficiency=0.95):
        self.num_panels = num_panels
        self.panel_capacity = panel_capacity  # Watts
        self.inverter_efficiency = inverter_efficiency
        self.total_capacity = num_panels * panel_capacity * inverter_efficiency / 1000  # kW

    def simulate_production(self, weather_data):
        # Base efficiency factors
        cloud_cover = weather_data.get('cloud', 0)
        temperature = weather_data.get('temperature', 25)
        condition = weather_data.get('condition', 'Clear').lower()

        # Adjust efficiency based on cloud cover and condition
        if 'clear' in condition or 'sunny' in condition:
            weather_factor = 1.0 - (cloud_cover / 100 * 0.5)
        elif 'cloudy' in condition or 'overcast' in condition:
            weather_factor = 0.7 - (cloud_cover / 100 * 0.3)
        elif 'rain' in condition:
            weather_factor = 0.5 - (cloud_cover / 100 * 0.2)
        else:
            weather_factor = 0.6  # Default factor for other conditions

        # Time-based factor (simulating sun position)
        now = datetime.now()
        hour = now.hour
        time_factor = max(0, min(1, (hour - 6) / 6)) if hour < 12 else max(0, min(1, (18 - hour) / 6))

        # Temperature factor (efficiency decreases with high temperatures)
        temp_factor = 1 - max(0, (temperature - 25) * 0.005)

        # Calculate production
        production = self.total_capacity * weather_factor * time_factor * temp_factor

        
        production *= random.uniform(0.95, 1.05)

        return round(production, 2)

    def simulate_consumption(self):
        # Simulate basic consumption pattern
        now = datetime.now()
        hour = now.hour

        # Base consumption
        base_consumption = self.total_capacity * 0.2

        # Add time-based variations
        if 6 <= hour < 9 or 17 <= hour < 22:
            # Higher consumption in morning and evening
            consumption = base_consumption * random.uniform(1.5, 2.5)
        elif 9 <= hour < 17:
            # Moderate consumption during the day
            consumption = base_consumption * random.uniform(1.0, 1.5)
        else:
            # Lower consumption at night
            consumption = base_consumption * random.uniform(0.5, 1.0)

        return round(consumption, 2)

    def get_system_health(self):
        # Simulate system health (0-100%)
        return random.randint(90, 100)
    def simulate_solar_energy_consumption(self):
        # Simulate solar energy consumption at a constant rate for a daily interval
        # Assuming a constant rate of 0.5 kWh per hour for a house
        daily_consumption = 0.5 * 24   # kWh

        # Initialize a storage mechanism (e.g., battery) to store excess energy
        self.storage_capacity = 10  # kWh (assuming a 10 kWh battery)
        self.current_storage = 0  # kWh

        # Simulate energy consumption and storage
        hourly_consumption = daily_consumption / 24
        for hour in range(24):
            energy_available = self.simulate_production({"cloud": 20, "temperature": 25, "condition": "Clear"})
            energy_consumed = min(hourly_consumption, energy_available)
            excess_energy = energy_available - energy_consumed

            # Store excess energy in the battery
            if excess_energy > 0:
                self.current_storage = min(self.storage_capacity, self.current_storage + excess_energy)

            # Consume energy from the battery if needed
            if energy_consumed > energy_available:
                energy_from_battery = min(self.current_storage, energy_consumed - energy_available)
                self.current_storage -= energy_from_battery
                energy_consumed -= energy_from_battery

            # Update the current storage level
            self.current_storage = max(0, self.current_storage - hourly_consumption)

        return daily_consumption
    

    def get_maintenance_prediction(self):
        # Simulate next maintenance date
        next_maintenance = datetime.now() + timedelta(days=random.randint(30, 180))
        return next_maintenance.strftime("%Y-%m-%d")

    def get_energy_data(self):
        # Return simulated data
        production = self.simulate_production({"cloud": 20, "temperature": 25, "condition": "Clear"})
        consumption = self.simulate_consumption()
        return {"production": production, "consumption": consumption}

    def get_device_status(self):
        
        return {"status": "simulated"}

def generate_hourly_data(pv_system, weather_condition, temperature):
    now = datetime.now()
    data = []


    for i in range(24):
        timestamp = (now - timedelta(hours=23-i)).strftime("%Y-%m-%d %H:%M:%S")
        production = pv_system.simulate_production(weather_condition, temperature)
        consumption = pv_system.simulate_consumption()
        data.append({



            "timestamp": timestamp,
            "production": production,
            "consumption": consumption
        })
    return data
