import os
import json
from tests.utils import fixtures_path
from hestia_earth.earth_engine.boundary import run, get_size_km2

fixtures_folder = os.path.join(fixtures_path, 'boundary')


def test_run_raster():
    with open(os.path.join(fixtures_folder, 'raster.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [
        44.02, 0.79, 0.08, 0.06, 0.03, 0.06, 0.08, 0.09, 0.04, 0.04, 0.05, 0.11, 0.07, 0.06, 0.93, 285.56, 283.89
    ]


def test_run_raster_different_scale():
    with open(os.path.join(fixtures_folder, 'raster-different-scale.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [
        43.94, 0.79, 0.08, 0.06, 0.03, 0.06, 0.08, 0.09, 0.04, 0.04, 0.05, 0.11, 0.07, 0.06, 0.93, 285.56, 283.89
    ]


def test_run_raster_missing_data():
    with open(os.path.join(fixtures_folder, 'raster-missing-data.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [15, 1.59, 31, 5, None, 0.29]


def test_run_raster_multiple():
    with open(os.path.join(fixtures_folder, 'raster-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r) for r in results] == [44, 1, 1, 43, 1, 1]


def test_run_vector():
    expected = '5180'

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
    expected = ['5180', 'PA0445', '5180', 'PA0402']

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


def test_get_size_km2():
    with open(os.path.join(fixtures_folder, 'boundary.json'), encoding='utf-8') as f:
        data = json.load(f)

    assert round(get_size_km2(data)) == 5284
