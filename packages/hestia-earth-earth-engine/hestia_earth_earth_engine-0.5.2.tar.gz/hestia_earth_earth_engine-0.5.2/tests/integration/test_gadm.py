import os
import json
from tests.utils import fixtures_path
from hestia_earth.earth_engine.gadm import run, get_size_km2

fixtures_folder = os.path.join(fixtures_path, 'gadm')


def test_run_raster():
    with open(os.path.join(fixtures_folder, 'raster.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [78, 0.14, 0.23, 294.21, 293.44]


def test_run_raster_missing_data():
    with open(os.path.join(fixtures_folder, 'raster-missing-data.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r, 2) for r in results] == [4, 0.32, 84, 5.1, 0.43, 0.3]


def test_run_raster_multiple():
    with open(os.path.join(fixtures_folder, 'raster-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert [r if r is None else round(r) for r in results] == [53, 3, 3, 42, 9, 1]


def test_run_vector():
    expected = '10435'

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
    expected = ['4647', 'PA0409', '5592', 'PA0445']

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
    assert round(get_size_km2('GADM-AUS.8.14_1')) == 78
