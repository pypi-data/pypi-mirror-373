import os
import ee

from .utils import EEType, use_geopandas, get_required_param, order_from_fields
from .utils.gee import get_point, bands_from_collections, batch_results, filter_first_or_empty

BATCH_SIZE = int(os.environ.get('EE_BATCH_SIZE_COORDINATES', '30'))


def _geometries(coordinates: list):
    return [get_point(longitude=coords.get('longitude'), latitude=coords.get('latitude')) for coords in coordinates]


def _vector_batch_processing(collections: list):
    def process(geometries: list):
        features = []
        for geometry in geometries:
            for collection in collections:
                field = collection.get('fields')
                feature = ee.FeatureCollection(collection.get('collection')).filterBounds(geometry)
                features.append(filter_first_or_empty(feature, field))
        results_order = order_from_fields(collections, geometries)
        return ee.FeatureCollection(features).set('band_order', results_order)
    return process


def _run_vector_ee(collections: list, coordinates: list):
    geometries = _geometries(coordinates)
    return batch_results(collections,
                         geometries,
                         _vector_batch_processing(collections),
                         batch_size=BATCH_SIZE)


def _run_vector(collections: list, coordinates: list):
    if use_geopandas():
        from .utils.vector import run_by_coordinates
        return run_by_coordinates(collections, coordinates)
    else:
        return _run_vector_ee(collections, coordinates)


def _raster_batch_processing(bands: ee.Image):
    def process(geometries: list):
        collection = ee.FeatureCollection(geometries)
        return bands.sampleRegions(collection=collection, scale=30)
    return process


def _run_raster(collections: list, coordinates: list):
    bands = bands_from_collections(collections, unmask=True)
    geometries = _geometries(coordinates)
    return batch_results(collections, geometries, _raster_batch_processing(bands), batch_size=BATCH_SIZE)


_RUN_BY_TYPE = {
    EEType.VECTOR.value: _run_vector,
    EEType.RASTER.value: _run_raster
}


def run(data: dict):
    ee_type = get_required_param(data, 'ee_type')
    collections = get_required_param(data, 'collections')
    coordinates = get_required_param(data, 'coordinates')
    return _RUN_BY_TYPE[ee_type](collections, coordinates)
