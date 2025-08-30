import os
from enum import Enum
from functools import reduce
from hestia_earth.utils.tools import non_empty_list


class EEType(Enum):
    RASTER = 'raster'
    VECTOR = 'vector'


def get_param(params: dict, key: str, default=None):
    value = params.get(key, default)
    return default if value is None else value


def get_required_param(params, key: str):
    if key not in params:
        raise KeyError(f"Missing required '{key}'")
    return params[key]


def parse_request_params(request):
    data = request.get_json(silent=True)
    return data if data is not None and len(data.keys()) > 0 else request.args


def get_fields_from_params(params: dict): return non_empty_list(get_param(params, 'fields', '').split(','))


def resolve(parts: list): return '/'.join(list(filter(lambda x: x is not None and len(x) > 0, parts)))


def float_precision(value): return float("{:.5f}".format(float(value) if isinstance(value, str) else value))


def use_geopandas(): return os.getenv('HEE_USE_GEOPANDAS', 'false') == 'true'


def order_from_fields(collections: list, geometries: list):
    return reduce(
        lambda prev, index: prev + [collections[index % len(collections)].get('fields')],
        range(0, len(geometries) * len(collections)),
        []
    )
