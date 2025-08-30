import ee
from functools import reduce
from hestia_earth.utils.tools import non_empty_list

from . import get_required_param, get_param

AREA_FIELD = 'areaKm2'
AREA_PERCENT_FIELD = 'areaKm2_percent'
GADM_COLLECTION_PREFIX = 'users/hestiaplatform/gadm36_'
MISSING_DATA_VALUE = -999999


def get_results(response: dict): return list(map(lambda f: f.get('properties'), response.get('features')))


def get_result(response: dict, key: str):
    results = get_results(response)
    result = results[0] if len(results) > 0 else {}
    return result.get(key, result.get('first'))


def get_result_key(collection: dict):
    return (
        collection.get('reducer') or
        collection.get('fields') or
        'mean'
    )


def _date_year(date: str): return int(date.split('-')[0])


def _id_to_level(id: str): return id.count('.')


def load_region(gadm_id: str = '', level: int = None):
    collection = ee.FeatureCollection(f"{GADM_COLLECTION_PREFIX}{level or _id_to_level(gadm_id)}")
    return collection.filterMetadata(
        f"GID_{_id_to_level(gadm_id)}", 'equals', gadm_id.replace('GADM-', '')
    ) if gadm_id else collection


def load_region_geometry(gadm_id: str): return load_region(gadm_id).geometry()


def get_point(coordinates: list = None, longitude: float = None, latitude: float = None):
    return ee.Geometry.Point(coordinates) if coordinates else ee.Geometry.Point(longitude, latitude)


def area_km2(geometry: ee.Geometry): return geometry.area().divide(1000 * 1000)


def _add_area(feature: ee.Feature): return feature.set({AREA_FIELD: area_km2(feature.geometry())})


def _intersect(geometry: ee.Geometry): return lambda feature: feature.intersection(geometry, 1)


def filter_first_or_empty(feature: ee.Feature, field: str):
    return ee.Algorithms.If(
        feature.size().eq(0),
        ee.Feature(None).set(field, 'None'),  # create empty feature with 'None' flag
        ee.Feature(None).copyProperties(feature.first(), [field])  # keep only the field we want
    )


def first_collection_by_area(collection: str, geometry: ee.Geometry, field: str):
    feature = ee.FeatureCollection(collection).filterBounds(geometry)
    return filter_first_or_empty(feature.map(_intersect(geometry)).map(_add_area).sort(AREA_FIELD, False), field)


GEOMETRY_BY_TYPE = {
    'FeatureCollection': lambda x: _get_geometry_by_type(x.get('features')[0]),
    'GeometryCollection': lambda x: _get_geometry_by_type(x.get('geometries')[0]),
    'Feature': lambda x: x.get('geometry'),
    'Polygon': lambda x: x,
    'MultiPolygon': lambda x: x
}


def _get_geometry_by_type(geojson): return GEOMETRY_BY_TYPE[geojson.get('type')](geojson)


def load_geometry(data: dict): return ee.Geometry(_get_geometry_by_type(data))


def _filter_or_empty(image: ee.ImageCollection, reducer_func):
    return ee.Algorithms.If(
        image.size().eq(0),
        ee.Image().unmask(MISSING_DATA_VALUE),
        image.reduce(reducer_func())
    )


def _filter_image_by_dates(image: ee.Image, dates: list, reducer_annual: str, reducer_period: str = 'mean'):
    # reducer applied for each tuple of dates
    reducer_annual_func = getattr(ee.Reducer, reducer_annual)
    collections = [
        _filter_or_empty(image.filterDate(start_date, end_date), reducer_annual_func) for start_date, end_date in dates
    ]

    # reducer applied for each collections
    reducer_period_func = getattr(ee.Reducer, reducer_period)
    return ee.ImageCollection(collections).reduce(reducer_period_func())


def _filter_image_by_years(
    image: ee.ImageCollection, start_date: str, end_date: str, reducer_annual: str, reducer_period: str
):
    start_year = _date_year(start_date)
    end_year = _date_year(end_date)
    dates = [(f"{year}-01-01", f"{year}-12-31") for year in range(start_year, end_year + 1)]
    return _filter_image_by_dates(image, dates, reducer_annual, reducer_period)


def _filter_image_by_year(image: ee.Image, year: str, reducer_annual: str):
    return _filter_image_by_dates(image, [(f"{year}-01-01", f"{year}-12-31")], reducer_annual)


def _image_from_collection(data: dict):
    collection = get_required_param(data, 'collection')
    band_name = get_param(data, 'band_name')
    is_image = get_param(data, 'is_image')
    image = ee.Image(collection) if is_image or not band_name else ee.ImageCollection(collection)
    image = image.select(band_name) if band_name else image

    reducer_annual = get_param(data, 'reducer_annual', 'sum')

    reducer_period = get_param(data, 'reducer_period')
    year = get_param(data, 'year')
    start_date = get_param(data, 'start_date')
    end_date = get_param(data, 'end_date')

    return _filter_image_by_years(image, start_date, end_date, reducer_annual, reducer_period) if all([
        start_date,
        end_date,
        reducer_period
    ]) else _filter_image_by_year(image, year, reducer_annual) if all([
        year
    ]) else _filter_image_by_dates(image, [(start_date, end_date)], reducer_annual) if all([
        start_date,
        end_date
    ]) else image


def bands_from_collections(collections: list, unmask: bool = False):
    """
    Get the list of bands to query from the collections.
    Note: when querying for coordinates, if one of the bands has no data, the result will be empty.
    """
    images = list(map(_image_from_collection, collections))
    bands = ee.ImageCollection.fromImages(images).toBands()
    return bands.unmask(MISSING_DATA_VALUE) if unmask else bands


def _combine_reducer(reducer, reducer_name: str):
    reducer_func = getattr(ee.Reducer, reducer_name)
    return reducer.combine(reducer2=reducer_func(), sharedInputs=True)


def combine_reducers(collections: list):
    reducers = list(set(non_empty_list([v.get('reducer') for v in collections])))
    return reduce(_combine_reducer, reducers[1:], getattr(ee.Reducer, reducers[0])()) if reducers else ee.Reducer.mode()


def _order_from_collection(index: int, collection: dict, with_reducer: bool):
    with_period = any([v in collection for v in ['year', 'start_date']])
    return '_'.join(non_empty_list([
        str(index),
        collection.get('band_name', 'b1'),
        '_'.join(non_empty_list([
            collection.get('reducer_annual'),
            collection.get('reducer_period', 'mean')  # also applied when no provided
        ])) if with_period else None,
        collection.get('reducer') if with_reducer else None
    ]))


def _order_from_collections(collections: list):
    reducers = set([v.get('reducer') for v in collections])
    return [_order_from_collection(i, c, len(reducers) > 1) for i, c in enumerate(collections)]


def _result_order(result: dict, collections: list):
    band_order = result.get('properties', {}).get('band_order', [])
    columns = [c for c in result.get('columns', {}).keys() if c != 'system:index']
    return band_order if len(band_order) > 0 else (
        columns if len(columns) == 1 else _order_from_collections(collections)
    )


def _property_value(value=None): return None if value is None or value == MISSING_DATA_VALUE else value


def _reduce_features(order: list):
    def process(values: list, feature: dict):
        properties = feature.get('properties', {})
        return values + [_property_value(properties.get(key)) for key in order]
    return process


def _reduce_features_order(features: list, orders: list):
    def process(values: list, index: int):
        properties = features[index].get('properties', {})
        order = orders[index]
        return values + [_property_value(properties.get(order))]
    return process


def _handle_none_values(features: list): return [None if f is None or f == 'None' else f for f in features]


def _process_batch(batch_func, collections: list, geometries: list):
    result = batch_func(geometries).getInfo()

    features = result.get('features', [])
    order = _result_order(result, collections)

    return _handle_none_values(
        [_property_value(features[0].get('properties', {}).get(key)) for key in order]
        if len(features) == 1 else
        reduce(_reduce_features_order(features, order), range(0, len(order)), [])
        if len(order) == len(features) else
        reduce(_reduce_features(order), features, [])
    )


def batch_results(collections: list, geometries: list, batch_func, batch_size: int):
    batches = range(0, len(geometries), batch_size)

    def reduce_batch(prev, curr: int):
        subset = geometries[curr:curr + batch_size]
        return prev + _process_batch(batch_func, collections, subset)

    return reduce(reduce_batch, batches, [])
