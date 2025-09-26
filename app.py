from flask import Flask, jsonify, render_template
import time

# def moving_vehicle(start_lat, start_lon, delta_lat=0.0001, delta_lon=0.0001, steps=50, delay=1):
#     """
#     Simulates a moving vehicle.
    
#     :param start_lat: Starting latitude
#     :param start_lon: Starting longitude
#     :param delta_lat: Change in latitude per step
#     :param delta_lon: Change in longitude per step
#     :param steps: Number of steps to move
#     :param delay: Delay in seconds between updates
#     """
#     lat, lon = start_lat, start_lon
#     for step in range(steps):
#         lat += delta_lat
#         lon += delta_lon
#         time.sleep(delay)  # Wait for a second (simulate real-time)
        
# # Example usage:
# moving_vehicle(28.6139, 77.2090)  # Delhi coordinates

app = Flask(__name__)
from math import radians, cos, sin, sqrt, atan2
import time

# --- Haversine ---
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# --- Moves between two points ---
class RouteMover:
    def __init__(self, start, end, speed_m_s=10):
        self.start = start
        self.end = end
        self.speed = speed_m_s
        self.current = start
        self.done = False
        self.total_distance = haversine(start, end)
        self.progress = 0.0

    def step(self):
        if self.done:
            return self.end

        self.progress += self.speed / self.total_distance
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done = True

        lat = self.start[0] + (self.end[0] - self.start[0]) * self.progress
        lon = self.start[1] + (self.end[1] - self.start[1]) * self.progress
        self.current = (lat, lon)
        return self.current

# --- BusRoute with pause at main cities ---
class BusRoute:
    def __init__(self, coordinates, main_cities_indices=None, speed=10, pause_sec=5):
        """
        coordinates: list of all coordinates (including intermediate points)
        main_cities_indices: list of indices of main cities in the coordinates list
        speed: meters per step
        pause_sec: how many seconds to pause at main cities
        """
        if len(coordinates) < 2:
            raise ValueError("Need at least 2 coordinates")
        self.coordinates = coordinates
        self.speed = speed
        self.current_index = 0
        self.pause_sec = pause_sec
        self.main_cities_indices = main_cities_indices or []
        self.pause_counter = 0  # counts steps while paused
        self.mover = RouteMover(coordinates[0], coordinates[1], speed)

    def step(self):
        # Check if we need to pause at main city
        if self.current_index in self.main_cities_indices and self.mover.done:
            if self.pause_counter < self.pause_sec:
                self.pause_counter += 1
                # Return the current position while paused
                return self.coordinates[self.current_index]
            else:
                self.pause_counter = 0  # reset pause counter

        lat, lon = self.mover.step()

        if self.mover.done:
            # Move to next coordinate
            self.current_index = (self.current_index + 1) % len(self.coordinates)
            next_index = (self.current_index + 1) % len(self.coordinates)
            self.mover = RouteMover(self.coordinates[self.current_index],
                                    self.coordinates[next_index],
                                    self.speed)
        return lat, lon

# Coordinates with main cities (include intermediate points for curves)
# Bus 1 loop
bus1_loop = [
    (31.6340, 74.8723),  # Amritsar
    (31.8186, 75.2025),  # Batala
    (32.0419, 75.4053),  # Gurdaspur
    (32.2730, 75.6522)   # Pathankot
]
# Bus 2 loop
bus2_loop = [
    (30.9000, 75.8573),  # Ludhiana
    (30.7055, 76.2206),  # Khanna
    (30.6746, 76.2912),  # Mandi Gobindgarh90
    (30.6422, 76.3840)   # Fatehgarh Sahib
]
# Bus 3 loop
bus3_loop = [
    (31.3260, 75.5762),  # Jalandhar
    (31.1275, 75.4750),  # Nakodar
    (31.0823, 75.3379),  # Shahkot
    (31.0184, 75.7911)   # Phillaur
]
# Bus 4 loop
bus4_loop = [
    (30.3398, 76.3869),  # Patiala
    (30.4786, 76.5941),  # Rajpura
    (30.3758, 76.1521),  # Nabha
    (30.1570, 76.1970)   # Samana
]
# Bus 5 loop
bus5_loop = [
    (30.3745, 75.5477),  # Barnala
    (30.3684, 75.8690),  # Dhuri
    (30.2451, 75.8420),  # Sangrur
    (30.1286, 75.7994)   # Sunam
]

# Main cities are at indices 0, 2, 4, 6
main_city_indices1 = [0, 1, 2, 3]
main_city_indices2 = [0, 1, 2, 3]
main_city_indices3 = [0, 1, 2, 3]
main_city_indices4 = [0, 1, 2, 3]
main_city_indices5 = [0, 1, 2, 3]


bus1 = BusRoute(bus1_loop, main_cities_indices=main_city_indices1, speed=1000, pause_sec=5)
bus2= BusRoute(bus2_loop, main_cities_indices=main_city_indices2, speed=1000, pause_sec=5)
bus3 = BusRoute(bus3_loop, main_cities_indices=main_city_indices3, speed=1000, pause_sec=5)
bus4 = BusRoute(bus4_loop, main_cities_indices=main_city_indices4, speed=1000, pause_sec=5)
bus5 = BusRoute(bus5_loop, main_cities_indices=main_city_indices5, speed=1000, pause_sec=5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_value')

def get_values():

    value1,value2=bus1.step()
    value3,value4=bus2.step()
    value5,value6=bus3.step()
    value7,value8=bus4.step()
    value9,value10=bus5.step()

    print(value1,value2)
    print(value3,value4)
    print(value5,value6)
    print(value7,value8)
    print(value9,value10)


    return jsonify({
    'value1': value1,
    'value2': value2,
    'value3': value3,
    'value4': value4,
    'value5': value5,
    'value6': value6,
    'value7': value7,
    'value8': value8,
    'value9': value9,
    'value10': value10
})

if __name__ == '__main__':
    app.run(debug=True)

