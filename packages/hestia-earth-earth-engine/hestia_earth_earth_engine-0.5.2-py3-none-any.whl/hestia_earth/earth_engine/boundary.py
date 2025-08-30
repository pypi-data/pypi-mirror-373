import os
import ee

from .utils import EEType, use_geopandas, get_required_param, order_from_fields
from .utils.gee import (
    load_geometry, area_km2,
    bands_from_collections,
    batch_results, combine_reducers,
    first_collection_by_area
)

BATCH_SIZE = int(os.environ.get('EE_BATCH_SIZE_BOUNDARY', '5000'))
SCALE = int(os.environ.get('EE_SCALE_BOUNDARY', '30'))


def get_size_km2(boundary: dict):
    return area_km2(load_geometry(boundary)).getInfo()


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


def _run_vector_ee(collections: list, boundaries: list):
    geometries = list(map(load_geometry, boundaries))
    return batch_results(collections,
                         geometries,
                         _vector_batch_processing(collections),
                         batch_size=BATCH_SIZE)


def _run_vector(collections: list, boundaries: list, *args):
    if use_geopandas():
        from .utils.vector import run_by_boundaries
        return run_by_boundaries(collections, boundaries)
    else:
        return _run_vector_ee(collections, boundaries)


def _batch_processing(bands: ee.Image, reducers: list, scale: int):
    def process(geometries: list):
        collection = ee.FeatureCollection(geometries)
        return bands.reduceRegions(**{
            'reducer': reducers,
            'collection': collection,
            'scale': scale,
        })
    return process


def _run_raster(collections: list, boundaries: list, scale: int):
    bands = bands_from_collections(collections, unmask=False)
    reducers = combine_reducers(collections)
    geometries = list(map(load_geometry, boundaries))
    return batch_results(collections, geometries, _batch_processing(bands, reducers, scale), batch_size=BATCH_SIZE)


_RUN_BY_TYPE = {
    EEType.VECTOR.value: _run_vector,
    EEType.RASTER.value: _run_raster
}


def run(data: dict):
    ee_type = get_required_param(data, 'ee_type')
    collections = get_required_param(data, 'collections')
    boundaries = get_required_param(data, 'boundaries')
    scale = data.get('scale') or SCALE
    return _RUN_BY_TYPE[ee_type](collections, boundaries, scale)
