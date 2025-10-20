import json
import os

class LocalStorage:
    cache_dir = os.path.join(
        os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
        "ChtnUniEnd"
    )
    os.makedirs(cache_dir, exist_ok=True)

    @staticmethod
    def write(name, data):
        file_path = os.path.join(LocalStorage.cache_dir, f"{name}.json")
        tmp_path = file_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f)
        os.replace(tmp_path, file_path)

    @staticmethod
    def read(name):
        file_path = os.path.join(LocalStorage.cache_dir, f"{name}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as f:
            return json.load(f)
