import os


def _get_container() -> str: return os.getenv('AZURE_STORAGE_CONTAINER_GEOSPATIAL')
