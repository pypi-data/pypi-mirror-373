from hestia_earth.schema import MeasurementMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
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
        "startDate": "",
        "endDate": "",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'potentialEvapotranspirationLongTermAnnualMean'
START_DATE = '1979-01-01'
END_DATE = '2020-12-31'
EE_PARAMS = {
    'collection': 'IDAHO_EPSCOR/TERRACLIMATE',
    'band_name': 'pet',
    'ee_type': 'raster',
    'reducer': 'mean',
    'reducer_annual': 'sum',
    'reducer_period': 'mean',
    'start_date': START_DATE,
    'end_date': END_DATE
}


def _measurement(value: float):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [value]
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    measurement['startDate'] = START_DATE
    measurement['endDate'] = END_DATE
    return measurement


def _download(site: dict):
    factor = 0.1
    value = download(TERM_ID, site, EE_PARAMS)
    return value * factor if value else None


def _run(site: dict):
    value = _download(site)
    return [_measurement(value)] if value is not None else []


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
