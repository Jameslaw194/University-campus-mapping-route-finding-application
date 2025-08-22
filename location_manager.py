from typing import Optional, List
from data import locations


class LocationManager:
    def get_coordinates(self, location_name: str) -> Optional[List[float]]:
        # Get the coordinates for a given location name
        for location in locations:
            if isinstance(location, list) and location[0][0] == location_name:
                return location[1]
        return None