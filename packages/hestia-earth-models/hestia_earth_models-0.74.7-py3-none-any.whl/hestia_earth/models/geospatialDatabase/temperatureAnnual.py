from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import max_date
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils.site import related_years
from .utils import to_celcius, download, has_geospatial_data, should_download
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
TERM_ID = 'temperatureAnnual'
EE_PARAMS = {
    'collection': 'ECMWF/ERA5_LAND/MONTHLY_AGGR',
    'band_name': 'temperature_2m',
    'ee_type': 'raster',
    'reducer': 'mean',
    'reducer_annual': 'mean'
}
BIBLIO_TITLE = 'ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate'


def _measurement(site: dict, value: float, year: int):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [value]
    measurement['startDate'] = f"{year}-01-01"
    measurement['endDate'] = max_date(f"{year}-12-31")
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _download(site: dict, year: int):
    return download(
        TERM_ID,
        site,
        {
            **EE_PARAMS,
            'year': str(year)
        }
    )


def _run(site: dict, year: int):
    value = to_celcius(_download(site, year))
    return _measurement(site, value, year) if value else None


def run(site: dict):
    contains_geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(TERM_ID, site)

    years = related_years(site)
    has_years = len(years) > 0

    logRequirements(site, model=MODEL, term=TERM_ID,
                    contains_geospatial_data=contains_geospatial_data,
                    below_max_area_size=below_max_area_size,
                    has_years=has_years,
                    years=';'.join(map(lambda y: str(y), years)))

    should_run = all([contains_geospatial_data, below_max_area_size, has_years])
    logShouldRun(site, MODEL, TERM_ID, should_run)

    return non_empty_list(map(lambda year: _run(site, year), years)) if should_run else []
