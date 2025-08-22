from datetime import datetime, timedelta
import folium
import os
import time
from typing import Tuple

from data import road_network
from path_calculation import PathCalculation


class MapManager:
    def __init__(self, path_calculation: PathCalculation):
        self.path_calculation = path_calculation

    def find_closest_node(self, latitude: float, longitude: float) -> int:
        # Find the closest node in the road network based on Haversine distance
        closest_node = None
        min_distance = float('inf')
        for i, node_info in enumerate(road_network):
            node_coords = node_info[1]
            distance = self.path_calculation.haversine_formula(latitude, longitude, node_coords[0], node_coords[1])
            if distance < min_distance:
                closest_node = i + 1  # Node numbering starts at 1
                min_distance = distance
        return closest_node if closest_node is not None else 1

    def generate_map(
        self,
        start_latitude: float,
        start_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        *,
        use_live_location: bool,
        speed_kmh: float,
        result_html_initial: str,
        start_name: str,
        destination_name: str,
        map_folder: str,
        navbar_template_path: str
    ) -> str:
        # Ensure map folder exists
        os.makedirs(map_folder, exist_ok=True)

        campus_map = folium.Map(
            location=[start_latitude, start_longitude],
            zoom_start=15,
            zoom_control=True,
            max_bounds=True,
            control_scale=True,
            prefer_canvas=True,
            tap=False,
        )

        # Determine start and destination nodes
        if use_live_location:
            start_node = self.find_closest_node(start_latitude, start_longitude)
        else:
            start_node = (self.path_calculation.coordinate_of_node(road_network, start_latitude, start_longitude) or 0) + 1

        destination_node = (self.path_calculation.coordinate_of_node(road_network, destination_latitude, destination_longitude) or 0) + 1

        line_distance = 0.0
        if use_live_location:
            # Draw line from live location to nearest road node
            coords1 = [start_latitude, start_longitude]
            coords2 = road_network[start_node - 1][1]
            folium.PolyLine(locations=[coords1, coords2], color='blue').add_to(campus_map)
            line_distance = self.path_calculation.haversine_formula(start_latitude, start_longitude, coords2[0], coords2[1])

        # Shortest path
        path, total_distance = self.path_calculation.dijkstras_algorithm(start_node, destination_node)
        total_distance = round(total_distance + line_distance, 2)

        # Time (minutes) and ETA
        total_time_min = round(((total_distance / max(speed_kmh, 0.1)) * 60), 1)
        eta = datetime.now() + timedelta(minutes=total_time_min)
        eta_str = eta.strftime('%H:%M')

        # Draw the path
        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]
            coords1 = road_network[current_node - 1][1]
            coords2 = road_network[next_node - 1][1]
            folium.PolyLine(locations=[coords1, coords2], color='blue').add_to(campus_map)

        # Room and floor information for destination
        room_and_floor_html = self.path_calculation.floors_and_rooms(
            destination_latitude, destination_longitude, result_html_initial
        )

        # Markers
        folium.Marker(
            [start_latitude, start_longitude],
            popup=folium.Popup(f'<font color="#1a33f0">Your location:</font><br>{start_name}')
        ).add_to(campus_map)

        folium.Marker(
            [destination_latitude, destination_longitude],
            popup=folium.Popup(
                f'<font color="#ff000d">Your Destination:</font><br>{destination_name}<br>{room_and_floor_html}',
                max_width=300
            )
        ).add_to(campus_map)

        # Save HTML
        html_filename = f'{int(time.time() * 1000)}.html'
        html_file_path = os.path.join(map_folder, html_filename)
        campus_map.save(html_file_path)

        # Update navbar placeholders
        with open(navbar_template_path, 'r') as navbar_file:
            navbar_contents = navbar_file.read()

        navbar_contents = navbar_contents.replace('{{ total_distance }}', f'Distance: {total_distance} km : ')
        navbar_contents = navbar_contents.replace('{{ total_time }}', f'Time: {total_time_min} min : ')
        navbar_contents = navbar_contents.replace('{{ eta }}', f'ETA: {eta_str}')

        # Combine navbar and map
        with open(html_file_path, 'r') as map_file:
            map_contents = map_file.read()
            combined_contents = navbar_contents + map_contents

        with open(html_file_path, 'w') as destination_file:
            destination_file.write(combined_contents)

        return html_filename