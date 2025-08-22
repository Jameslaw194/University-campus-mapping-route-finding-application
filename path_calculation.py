import math
from typing import List, Tuple, Optional
from data import road_network, room_numbers


class PathCalculation:
    def haversine_formula(self, lat1: float, long1: float, lat2: float, long2: float) -> float:
        # Calculate the Haversine distance between two sets of latitude and longitude coordinates
        lat1 = math.radians(lat1)
        long1 = math.radians(long1)
        lat2 = math.radians(lat2)
        long2 = math.radians(long2)

        delta_lat = lat2 - lat1
        delta_long = long2 - long1

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_long / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius_of_earth_km = 6371
        return radius_of_earth_km * c

    def dijkstras_algorithm(self, start_node: int, end_node: int) -> Tuple[List[int], float]:
        # Dijkstra's algorithm to find the shortest path between the start_node and end_node
        num_nodes = len(road_network)
        distances = {node: float('inf') for node in range(1, num_nodes + 1)}
        previous_nodes = {node: None for node in range(1, num_nodes + 1)}

        distances[start_node] = 0
        visited = set()
        unvisited_nodes = set(range(1, num_nodes + 1))

        while unvisited_nodes:
            current_node = min(unvisited_nodes, key=lambda node: distances[node])
            unvisited_nodes.remove(current_node)

            for neighbor in road_network[current_node - 1][0]:
                if neighbor not in visited:
                    distance = distances[current_node] + self.haversine_formula(
                        *road_network[current_node - 1][1], *road_network[neighbor - 1][1]
                    )
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_node
            visited.add(current_node)

        path: List[int] = []
        current: Optional[int] = end_node
        total_distance = 0.0
        while current is not None:
            path.insert(0, current)
            if previous_nodes[current] is not None:
                total_distance += self.haversine_formula(
                    *road_network[current - 1][1], *road_network[previous_nodes[current] - 1][1]
                )
            current = previous_nodes[current]

        return path, total_distance

    def coordinate_of_node(self, network: list, latitude: float, longitude: float) -> Optional[int]:
        # Find the index of the node in the road network with the specified coordinates
        for entry in network:
            if entry[1] == [latitude, longitude]:
                return network.index(entry)
        return None

    def floors_and_rooms(self, destination_latitude: float, destination_longitude: float, result: str) -> str:
        # Find and format floor and room information for a given destination coordinates
        for entry in room_numbers:
            coordinates = entry[0]
            rooms_info = entry[1]
            if coordinates[0] == destination_latitude and coordinates[1] == destination_longitude:
                result += "<style>"
                result += ".scrollable-popup {max-height: 200px; overflow-y: auto;}"
                result += "table {width: 100%; border-collapse: collapse;}"
                result += "th, td {border: 1px solid #ddd; padding: 8px;}"
                result += "tr:nth-child(even) {background-color: #f2f2f2;}"
                result += "th {padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #4CAF50; color: white;}"
                result += "</style>"
                result += "<div class='scrollable-popup'>"
                result += "<table>"
                result += "<tr><th>Floor:</th><th>Rooms:</th></tr>"
                for floor, rooms in rooms_info:
                    floor_number = floor[0]
                    room_numbers_str = '<br>'.join(map(str, rooms))
                    result += f"<tr><td>{floor_number}</td><td>{room_numbers_str}</td></tr>"
                result += "</table>"
                result += "</div>"
        return result