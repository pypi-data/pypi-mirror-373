# HESTIA Engine Models

[![Pipeline Status](https://gitlab.com/hestia-earth/hestia-engine-models/badges/master/pipeline.svg)](https://gitlab.com/hestia-earth/hestia-engine-models/commits/master)
[![Coverage Report](https://gitlab.com/hestia-earth/hestia-engine-models/badges/master/coverage.svg)](https://gitlab.com/hestia-earth/hestia-engine-models/commits/master)

HESTIA's set of models for running calculations or retrieving data using external datasets and internal lookups.

## Documentation

Documentation for every model can be found in the [HESTIA API Documentation](https://hestia.earth/docs/#hestia-calculation-models).

## Install

1. Install python `3` (we recommend using python `3.6` minimum)
2. Install the module:
```bash
pip install hestia_earth.models
```
3. Set the following environment variables:
```
API_URL=https://api.hestia.earth
WEB_URL=https://hestia.earth
```

### Usage

```python
from hestia_earth.models.pooreNemecek2018 import run

cycle_data = {"@type": "Cycle", ...}
# cycle is a JSONLD node Cycle
result = run('no3ToGroundwaterSoilFlux', cycle_data)
print(result)
```

This will display only the result of the `no3ToGroundwaterSoilFlux` model (Emission).

Additionally, to reduce the number of queries to the HESTIA API and run the models faster, prefetching can be enabled:
```python
from hestia_earth.models.preload_requests import enable_preload

enable_preload()
```

#### Using the orchestrator

The models come with an "orchestrator", which allows you to run a pre-configured set of models instead of a single one.

The configuration for each Node (Cycle, Site or ImpactAssessment) can be found in the [config](./config) folder.

Usage:
```python
from hestia_earth.orchestrator import run
from hestia_earth.models.config import load_config

cycle_data = {"@type": "Cycle", ...}
result = run(cycle, load_config(cycle))
print(result)
```

This will display the Cycle recalculated with all HESTIA default models running.

#### Using Spatial Models

We have models that can gap-fill geographical information on a `Site`. If you want to use these models:
1. Install the library: `pip install hestia_earth.earth_engine`
2. Follow the [Getting Started instructions](https://gitlab.com/hestia-earth/hestia-earth-engine#getting-started).

#### Using the ecoinventV3 model

ecoinvent is a consistent, transparent, and well validated life cycle inventory database.
We use ecoinvent data to ascertain the environmental impacts of activities that occur outside of our system boundary, for example data on the environmental impacts of extracting oil and producing diesel, or the impacts of manufacturing plastics.

The `ecoinventV3` model requires a valid [license](https://ecoinvent.org/offerings/licences/) to run. We are currently working on a way to enable users of this code with a valid ecoinvent licence to run these models themselves, but for now, these models are only available on the public platform.
