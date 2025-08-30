from hestia_earth.utils.storage._s3_client import _load_from_bucket, _exists_in_bucket
from hestia_earth.utils.storage._local_client import _exists_in_folder
from hestia_earth.utils.storage._azure_client import _load_from_container, _exists_in_container

from ._s3_client import _get_bucket
from ._azure_client import _get_container
from ._local_client import _get_folder, _load_from_folder


def load_from_storage(filepath: str):
    if _get_bucket():
        return _load_from_bucket(_get_bucket(), filepath)
    if _get_container():
        return _load_from_container(_get_container(), filepath)
    if _get_folder():
        return _load_from_folder(_get_folder(), filepath)
    raise ImportError


def file_exists(filepath: str, ) -> bool:
    if _get_bucket():
        return _exists_in_bucket(_get_bucket(), filepath)
    if _get_container():
        return _exists_in_container(_get_container(), filepath)
    if _get_folder():
        return _exists_in_folder(_get_folder(), filepath)
    raise ImportError
