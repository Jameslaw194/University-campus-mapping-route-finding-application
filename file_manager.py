import os
import time


class FileManager:
    def delete_old_map_files(self, map_folder: str) -> None:
        # Delete map files older than 24 hours in the provided map_folder directory
        current_time = time.time()
        one_day_ago = current_time - 24 * 60 * 60  # 24 hours

        if not os.path.isdir(map_folder):
            return

        for root, dirs, files in os.walk(map_folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_creation_time = os.path.getctime(file_path)
                    if file_creation_time < one_day_ago:
                        os.remove(file_path)
                except FileNotFoundError:
                    # File might have been deleted concurrently
                    pass