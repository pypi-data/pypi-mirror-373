import os


def _get_folder() -> str:
    folder = os.getenv('EARTH_ENGINE_GEOSPATIAL_FOLDER', './geospatial')
    os.makedirs(folder, exist_ok=True)
    return folder


def _load_from_folder(folder: str, key: str):
    try:
        with open(os.path.join(folder, key), 'rb') as f:
            return f.read()
    except Exception:
        # in case the file does not exist, should simply return None
        return None
