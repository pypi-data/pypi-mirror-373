from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.source import get_source
from .utils import download, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "",
        "depthLower": "",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'soilPh'
EE_PARAMS = [
    {
        'collection': 'T_PH_H2O_v2_depth_1',
        'ee_type': 'raster',
        'reducer': 'mean',
        'depthUpper': 0,
        'depthLower': 20
    },
    {
        'collection': 'T_PH_H2O_v2_depth_2',
        'ee_type': 'raster',
        'reducer': 'mean',
        'depthUpper': 20,
        'depthLower': 40
    },
    {
        'collection': 'T_PH_H2O_v2_depth_3',
        'ee_type': 'raster',
        'reducer': 'mean',
        'depthUpper': 40,
        'depthLower': 60
    },
    {
        'collection': 'T_PH_H2O_v2_depth_4',
        'ee_type': 'raster',
        'reducer': 'mean',
        'depthUpper': 60,
        'depthLower': 80
    }
]
BIBLIO_TITLE = 'Harmonized World Soil Database Version 2.0.'


def _measurement(site: dict, value: int, depthUpper: int, depthLower: int):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [value]
    measurement['depthUpper'] = depthUpper
    measurement['depthLower'] = depthLower
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _run_depths(site: dict, params: dict):
    value = download(TERM_ID, site, params)
    return None if value is None else (
        _measurement(site, round(value, 7), params.get('depthUpper'), params.get('depthLower'))
    )


def _run(site: dict):
    return non_empty_list([_run_depths(site, params) for params in EE_PARAMS])


def _should_run(site: dict):
    contains_geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(TERM_ID, site)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    contains_geospatial_data=contains_geospatial_data,
                    below_max_area_size=below_max_area_size)

    should_run = all([contains_geospatial_data, below_max_area_size])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
