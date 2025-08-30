import json
import os
from tests.utils import fixtures_path
from hestia_earth.earth_engine import merge_region_geometries


def test_merge_region_geometries():
    region_ids = ['GADM-IRN.21_1', 'GADM-IRN.24_1', 'GADM-IRN.27_1']

    with open(os.path.join(fixtures_path, 'merged-regions.json'), encoding='utf-8') as f:
        expected = json.load(f)

    result = merge_region_geometries(region_ids)
    assert result == expected
