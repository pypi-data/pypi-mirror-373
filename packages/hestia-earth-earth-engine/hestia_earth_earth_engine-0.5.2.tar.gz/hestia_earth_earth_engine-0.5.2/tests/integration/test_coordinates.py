import os
import json
from tests.utils import fixtures_path

from hestia_earth.earth_engine.coordinates import run

fixtures_folder = os.path.join(fixtures_path, 'coordinates')


def test_run_raster():
    with open(os.path.join(fixtures_folder, 'raster.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [81, 786, 0.95, 1.26, 297.13, 296.59]


def test_run_raster_missing_data():
    with open(os.path.join(fixtures_folder, 'raster-missing-data.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [15, 1.59, 31, 5, None, 0.29]


def test_run_raster_multiple():
    with open(os.path.join(fixtures_folder, 'raster-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r) for r in results] == [66, 2, 12, 64, 2, 11]


def test_run_vector():
    expected = '9692'

    os.environ['HEE_USE_GEOPANDAS'] = 'true'
    with open(os.path.join(fixtures_folder, 'vector.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert results[0] == expected

    os.environ['HEE_USE_GEOPANDAS'] = 'false'
    with open(os.path.join(fixtures_folder, 'vector-ee.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert results[0] == expected


def test_run_vector_multiple():
    expected = ['9135', 'NT0704', '9692', 'NT0704']

    os.environ['HEE_USE_GEOPANDAS'] = 'true'
    with open(os.path.join(fixtures_folder, 'vector-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    values = run(data)
    assert values == expected

    os.environ['HEE_USE_GEOPANDAS'] = 'false'
    with open(os.path.join(fixtures_folder, 'vector-ee-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    values = run(data)
    assert values == expected


def test_run_vector_ee_multiple_gadm():
    expected = [
        None, 'BRA', 'BRA.5_1', 'BRA.5.136_1', 'BRA.5.136.1_1', None,
        'FRA.1.2.2.1.2_1', 'FRA', 'FRA.1_1', 'FRA.1.2_1', 'FRA.1.2.2_1', 'FRA.1.2.2.1_1'
    ]

    os.environ['HEE_USE_GEOPANDAS'] = 'false'
    with open(os.path.join(fixtures_folder, 'vector-ee-multiple-gadm.json'), encoding='utf-8') as f:
        data = json.load(f)

    values = run(data)
    assert values == expected
