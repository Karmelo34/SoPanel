import random
from datetime import datetime
import socket
import json
import threading
import time

class SolarDeviceSimulator:
    def __init__(self, device_id, device_type, ip, port):
        self.device_id = device_id
        self.device_type = device_type
        self.ip = ip
        self.port = port
        self.connected = False
        self.panel_capacity = 300  # Watts
        self.num_panels = 20
        self.total_capacity = self.panel_capacity * self.num_panels / 1000  # kW

    def generate_data(self):
        now = datetime.now()
        hour = now.hour

        base_irradiance = max(0, min(1000, (hour - 6) * 100)) if 6 <= hour < 18 else 0
        irradiance = base_irradiance * random.uniform(0.8, 1.2)
        temperature = 20 + random.uniform(-5, 10)
        production_factor = min(1, irradiance / 1000) * (1 - max(0, (temperature - 25) * 0.005))
        energy_production = self.total_capacity * production_factor * random.uniform(0.9, 1.1)

        return {
            "timestamp": now.isoformat(),
            "device_id": self.device_id,
            "device_type": self.device_type,
            "energy_production": round(energy_production, 2),
            "solar_irradiance": round(irradiance, 2),
            "panel_temperature": round(temperature, 2),
            "ambient_temperature": round(temperature - random.uniform(2, 5), 2),
            "efficiency": round(production_factor * 100, 2),
            "weather_condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]),
            "system_status": random.choice(["Normal", "Normal", "Normal", "Warning"])
        }

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)
        print(f"Solar device simulator {self.device_id} listening on {self.ip}:{self.port}")
        
        threading.Thread(target=self.discovery_broadcast, daemon=True).start()
        
        while True:
            conn, addr = self.socket.accept()
            self.connected = True
            print(f"Connected by {addr}")
            while self.connected:
                data = self.generate_data()
                conn.sendall(json.dumps(data).encode())
                time.sleep(5)  # Send data every 5 seconds
            conn.close()

    def discovery_broadcast(self):
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        discovery_socket.bind(("", 0))
        while True:
            discovery_data = {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "ip": self.ip,
                "port": self.port
            }
            discovery_socket.sendto(json.dumps(discovery_data).encode(), ('<broadcast>', 5000))
            time.sleep(10)  # Broadcast every 10 seconds

if __name__ == "__main__":
    # Simulate multiple devices
    devices = [
        SolarDeviceSimulator("SIM001", "solar_panel", "127.0.0.1", 5001),
        SolarDeviceSimulator("SIM002", "inverter", "127.0.0.1", 5002),
        SolarDeviceSimulator("SIM003", "battery", "127.0.0.1", 5003)
    ]
    
    for device in devices:
        threading.Thread(target=device.start, daemon=True).start()
    
    # Keep the main thread alive
    while True:
        time.sleep(1)
