import os


def _get_bucket() -> str: return os.getenv('AWS_BUCKET_GEOSPATIAL')
