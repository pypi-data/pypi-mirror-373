from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import flatten, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import slice_by_year
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {"@type": "Measurement", "term.id": "rainfallMonthly"}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "startDate": "",
        "endDate": "",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'rainfallAnnual'
MEASUREMENT_ID = 'rainfallMonthly'


def _measurement(value: float, start_date: str, end_date: str):
    data = _new_measurement(TERM_ID, MODEL)
    data['value'] = [value]
    data['startDate'] = start_date
    data['endDate'] = end_date
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data


def _run(measurement: dict):
    values = measurement.get('value', [])
    dates = measurement.get('dates', [])
    term_id = measurement.get('term', {}).get('@id')
    results = slice_by_year(term_id, dates, values)
    return [_measurement(value, start_date, end_date) for (value, start_date, end_date) in results]


def _should_run(site: dict):
    measurements = [m for m in site.get('measurements', []) if m.get('term', {}).get('@id') == MEASUREMENT_ID]
    has_monthly_measurements = len(measurements) > 0

    logRequirements(site, model=MODEL, term=TERM_ID,
                    has_monthly_measurements=has_monthly_measurements)

    should_run = all([has_monthly_measurements])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, measurements


def run(site: dict):
    should_run, measurements = _should_run(site)
    return non_empty_list(flatten(map(_run, measurements))) if should_run else []
