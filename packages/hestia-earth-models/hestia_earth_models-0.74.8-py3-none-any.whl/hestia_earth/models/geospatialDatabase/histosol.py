from hestia_earth.schema import MeasurementMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement, total_other_soilType_value
from hestia_earth.models.utils.source import get_source
from .utils import download, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ],
        "none": {
            "measurements": [{
                "@type": "Measurement",
                "value": "100",
                "depthUpper": "0",
                "depthLower": "30",
                "term.termType": "soilType"
            }]
        }
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'histosol'
EE_PARAMS = {
    'collection': 'histosols_corrected',
    'ee_type': 'raster',
    'reducer': 'mean'
}
BIBLIO_TITLE = 'Harmonized World Soil Database Version 1.2. Food and Agriculture Organization of the United Nations (FAO).'  # noqa: E501


def _measurement(site: dict, value: float):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [round(value, 7)]
    measurement['depthUpper'] = 0
    measurement['depthLower'] = 30
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _run(site: dict):
    value = download(TERM_ID, site, EE_PARAMS)
    return [_measurement(site, value)] if value is not None else []


def _should_run(site: dict):
    contains_geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(TERM_ID, site)

    total_measurements_value = total_other_soilType_value(site.get('measurements', []), TERM_ID)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    contains_geospatial_data=contains_geospatial_data,
                    below_max_area_size=below_max_area_size,
                    total_soilType_measurements_value=total_measurements_value,
                    total_soilType_measurements_value_is_0=total_measurements_value == 0)

    should_run = all([contains_geospatial_data, below_max_area_size, total_measurements_value == 0])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
