import os
import ee

from .utils import EEType, use_geopandas, get_required_param, order_from_fields
from .utils.gee import (
    load_region, load_region_geometry, area_km2, get_point,
    bands_from_collections,
    batch_results, combine_reducers,
    first_collection_by_area
)

BATCH_SIZE = int(os.environ.get('EE_BATCH_SIZE_GADM', '5000'))
SCALE = int(os.environ.get('EE_SCALE_GADM', '30'))


def get_size_km2(gadm_id: str): return area_km2(load_region_geometry(gadm_id)).getInfo()


def get_distance_to_coordinates(gadm_id: str, latitude: float, longitude: float):
    """
    Returns the distance between the coordinates and the GADM region, in meters.
    """
    coordinates = get_point(longitude=longitude, latitude=latitude)
    return load_region_geometry(gadm_id).distance(coordinates).getInfo()


def get_id_by_coordinates(level: int, latitude: float, longitude: float):
    """
    Returns the GADM ID of the closest region to the coordinates by level (0 to 5).
    """
    collection = load_region(level=level)
    coordinates = get_point(longitude=longitude, latitude=latitude)
    region = collection.filterBounds(coordinates).first()
    return region.get(f"GID_{level}").getInfo()


def _vector_batch_processing(collections: list):
    def process(geometries: list):
        features = []
        for geometry in geometries:
            for collection in collections:
                field = collection.get('fields')
                features.append(first_collection_by_area(collection.get('collection'), geometry, field))
        results_order = order_from_fields(collections, geometries)
        return ee.FeatureCollection(features).set('band_order', results_order)
    return process


def _run_vector_ee(collections: list, gadm_ids: list):
    geometries = list(map(load_region_geometry, gadm_ids))
    return batch_results(collections,
                         geometries,
                         _vector_batch_processing(collections),
                         batch_size=BATCH_SIZE)


def _run_vector(collections: list, gadm_ids: list, *args):
    if use_geopandas():
        from .utils.vector import run_by_gadm_ids
        return run_by_gadm_ids(collections, gadm_ids)
    else:
        return _run_vector_ee(collections, gadm_ids)


def _batch_processing(bands: ee.Image, reducers: list, scale: int):
    def process(geometries: list):
        collection = ee.FeatureCollection(geometries)
        return bands.reduceRegions(**{
            'reducer': reducers,
            'collection': collection,
            'scale': scale,
        })
    return process


def _run_raster(collections: list, gadm_ids: list, scale: int):
    bands = bands_from_collections(collections, unmask=False)
    reducers = combine_reducers(collections)
    geometries = list(map(load_region_geometry, gadm_ids))
    return batch_results(collections, geometries, _batch_processing(bands, reducers, scale), batch_size=BATCH_SIZE)


_RUN_BY_TYPE = {
    EEType.VECTOR.value: _run_vector,
    EEType.RASTER.value: _run_raster
}


def run(data: dict):
    ee_type = get_required_param(data, 'ee_type')
    collections = get_required_param(data, 'collections')
    gadm_ids = get_required_param(data, 'gadm-ids')
    scale = data.get('scale') or SCALE
    return _RUN_BY_TYPE[ee_type](collections, gadm_ids, scale)
