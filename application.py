from map_manager import MapManager
from location_manager import LocationManager
from file_manager import FileManager
from path_calculation import PathCalculation


class Application:
    def __init__(self, map_folder: str | None = None, favicon_directory: str | None = None):
        # Managers and utilities
        self.path_calculation = PathCalculation()
        self.map_manager = MapManager(self.path_calculation)
        self.location_manager = LocationManager()
        self.file_manager = FileManager()

        # Start/destination state
        self.start_latitude: float | None = None
        self.start_longitude: float | None = None
        self.start_name: str = ''
        self.destination_latitude: float | None = None
        self.destination_longitude: float | None = None
        self.destination_name: str = ''

        # Live location and speed (km/h)
        self.live_location: bool = False
        self.speed: float = 4.8

        # Result HTML and generated map filename
        self.result: str = ''
        self.html_filename: str | None = None

        # Paths (to be set by the Flask app)
        self.map_folder: str | None = map_folder
        self.favicon_directory: str | None = favicon_directory