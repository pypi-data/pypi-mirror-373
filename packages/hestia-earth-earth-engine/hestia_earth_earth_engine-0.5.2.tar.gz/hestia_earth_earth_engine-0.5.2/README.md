# Hestia Earth Engine

[![Pipeline Status](https://gitlab.com/hestia-earth/hestia-earth-engine/badges/master/pipeline.svg)](https://gitlab.com/hestia-earth/hestia-earth-engine/commits/master)
[![Coverage Report](https://gitlab.com/hestia-earth/hestia-earth-engine/badges/master/coverage.svg)](https://gitlab.com/hestia-earth/hestia-earth-engine/commits/master)

Hestia's utilities to make queries to Earth Engine.

## Getting Started

1. Sign up for a [Google Cloud Account](https://cloud.google.com)
2. Enable the [Earth Engine API](https://developers.google.com/earth-engine)
3. Create a [Service Account with Earth Engine access](https://developers.google.com/earth-engine/guides/service_account)
4. Set the service account JSON credentials in the following file: `ee-credentials.json`
5. Set the following environment variable:
```
# path to the ee-credentials.json file saved at previous step
EARTH_ENGINE_KEY_FILE=./ee-credentials.json
```

## Install

1. Install Python `3` (we recommend using Python `3.6` minimum)
2. Install the module:
```bash
pip install hestia_earth.earth_engine
```

### Usage

```python
from hestia_earth.earth_engine import init_gee, run

# call this only once during a session
init_gee()
# fetch sand content for a specific location
data = {
  "ee_type": "raster",
  "collections": [
    {
      "collection": "users/hestiaplatform/T_SAND",
      "fields": "first"
    }
  ],
  "coordinates": [
    {
      "latitude": -11.77,
      "longitude": -45.7689
    }
  ]
}
result = run(data)
assert result == [81]
```
