from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import flatten, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import first_day_of_month, last_day_of_month
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils.site import related_years
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
        "dates": "",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'precipitationMonthly'
EE_PARAMS = {
    'collection': 'ECMWF/ERA5_LAND/MONTHLY_AGGR',
    'band_name': 'total_precipitation_sum',
    'ee_type': 'raster',
    'reducer': 'mean',
    'reducer_annual': 'sum'
}
BIBLIO_TITLE = 'ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate'


def _measurement(site: dict, value: list, dates: list):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = value
    measurement['dates'] = dates
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _download(site: dict,  start_date: str, end_date: str):
    return download(
        TERM_ID,
        site,
        {
            **EE_PARAMS,
            'start_date': start_date,
            'end_date': end_date
        }
    )


def _value_at(site: dict, start_date: str, end_date: str):
    # collection is in meters, convert to millimeters
    factor = 1000
    value = _download(site, start_date, end_date)
    return (value * factor, start_date[0:7]) if value is not None else None


def _run(site: dict, years: list):
    # fetch from first year to last
    years = range(years[0], years[-1] + 1) if len(years) > 1 else years

    dates = flatten([
        [
            (first_day_of_month(year, month).strftime('%Y-%m-%d'), last_day_of_month(year, month).strftime('%Y-%m-%d'))
            for month in range(1, 13)
        ] for year in years
    ])
    values = non_empty_list([_value_at(site, start_date, end_date) for start_date, end_date in dates])
    return [_measurement(site, [v for v, d in values], [d for v, d in values])] if values else []


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

    return _run(site, years) if should_run else []
