from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.source import get_source
from .utils import download, get_region_factor, has_geospatial_data, should_download
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
        "description": "",
        "methodClassification": "geospatial dataset"
    }]
}
LOOKUPS = {
    "region-measurment": "ecoClimateZone"
}
TERM_ID = 'ecoClimateZone'
EE_PARAMS = {
    'collection': 'climate_zone',
    'ee_type': 'raster',
    'reducer': 'mode'
}
BIBLIO_TITLE = 'Biofuels: a new methodology to estimate GHG emissions from global land use change'


def _measurement(site: dict, value: int):
    measurement = _new_measurement(TERM_ID)
    measurement['description'] = _name(value)
    measurement['value'] = [value]
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _name(value: int):
    lookup = download_lookup(f"{TERM_ID}.csv")
    return _get_single_table_value(lookup, column_name(TERM_ID), value, 'name')


def _run(site: dict):
    value = download(TERM_ID, site, EE_PARAMS)
    return [_measurement(site, round(value))] if value is not None else []


def _run_default(site: dict):
    region_factor = get_region_factor(TERM_ID, site)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    region_factor=region_factor)

    should_run = all([region_factor])
    logShouldRun(site, MODEL, TERM_ID, should_run, run_by='Lookup')
    return [_measurement(site, round(region_factor))] if should_run else []


def _should_run(site: dict):
    contains_geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(TERM_ID, site)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    contains_geospatial_data=contains_geospatial_data,
                    below_max_area_size=below_max_area_size)

    should_run = all([contains_geospatial_data, below_max_area_size])
    logShouldRun(site, MODEL, TERM_ID, should_run, run_by='Earth Engine')
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else _run_default(site)
