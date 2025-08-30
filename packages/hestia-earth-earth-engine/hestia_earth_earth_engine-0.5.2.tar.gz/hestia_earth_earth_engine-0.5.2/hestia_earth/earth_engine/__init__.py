from pkgutil import extend_path
import os
from functools import reduce
import ee
from enum import Enum
from hestia_earth.utils.tools import current_time_ms

from .log import logger
from .boundary import run as run_boundary
from .coordinates import run as run_coordinates
from .gadm import run as run_gadm
from .utils.gee import load_region

__path__ = extend_path(__path__, __name__)

EE_ACCOUNT_ID = os.getenv('EARTH_ENGINE_ACCOUNT_ID')
EE_KEY_FILE = os.getenv('EARTH_ENGINE_KEY_FILE', 'ee-credentials.json')


def init_gee(high_volume: bool = False):
    now = current_time_ms()
    logger.debug(f"initializing ee using {EE_KEY_FILE}...")
    opt_url = 'https://earthengine-highvolume.googleapis.com' if high_volume else 'https://earthengine.googleapis.com'
    ee.Initialize(
        credentials=ee.ServiceAccountCredentials(EE_ACCOUNT_ID, EE_KEY_FILE),
        opt_url=opt_url
    )
    logger.debug(f"done initializing ee in {current_time_ms() - now} ms")


class RunType(Enum):
    BOUNDARY = 'boundary'
    COORDINATES = 'coordinates'
    GADM = 'gadm'


RUN_BY_TYPE = {
    RunType.BOUNDARY: lambda v: run_boundary(v),
    RunType.COORDINATES: lambda v: run_coordinates(v),
    RunType.GADM: lambda v: run_gadm(v)
}


def _get_run_type(data: dict):
    if data.get('coordinates'):
        return RunType.COORDINATES
    if data.get('boundaries'):
        return RunType.BOUNDARY
    if data.get('gadm-ids'):
        return RunType.GADM
    raise Exception('Unkown type. Please use either `coordinates`, `boundaries` or `gadm-ids` param.')


def run(data: dict):
    """
    Run query against Google Earth Engine.
    This is specifically designed to work along the Hestia Engine Models library.

    Parameters
    ----------
    data : dict
        The parameters needed to run the queries.

    Returns
    -------
    dict
        The result from Earth Engine query.
    """
    now = current_time_ms()
    result = RUN_BY_TYPE.get(_get_run_type(data), lambda v: v)(data)
    logger.info('time=%s, unit=ms', current_time_ms() - now)
    return result


def merge_region_geometries(region_ids: list) -> dict:
    """
    Merge multiple regions together to form a single Polygon.

    Parameters
    ----------
    region_ids : list of string
        A list of GADM region `@id`.

    Returns
    -------
    dict
        The union of the Polygons as a Polygon or MultiPolygon if those regions don't connect fully.
    """
    geometries = [load_region(id).geometry() for id in region_ids]
    return reduce(lambda a, b: a.union(b), geometries[1:], geometries[0]).getInfo()
