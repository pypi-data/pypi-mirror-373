from datetime import timedelta
from hestia_earth.utils.date import is_in_days, is_in_months
from hestia_earth.utils.tools import safe_parse_date

from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "optional": {
            "startDate": "month precision",
            "endDate": "day precision",
            "cycleDuration": ""
        }
    }
}
RETURNS = {
    "The startDate as a string": ""
}
MODEL_KEY = 'startDate'


def _run_by_cycleDuration(cycle: dict):
    endDate = safe_parse_date(cycle.get('endDate'))
    cycleDuration = cycle.get('cycleDuration')
    return (endDate - timedelta(days=cycleDuration)).strftime('%Y-%m-%d')


def _should_run_by_cycleDuration(cycle: dict):
    has_endDate = cycle.get('endDate') is not None
    has_endDate_day_precision = has_endDate and is_in_days(cycle.get('endDate'))
    has_cycleDuration = cycle.get('cycleDuration') is not None

    logRequirements(cycle, model=MODEL, key=MODEL_KEY, by='cycleDuration',
                    has_endDate=has_endDate,
                    has_endDate_day_precision=has_endDate_day_precision,
                    has_cycleDuration=has_cycleDuration)

    should_run = all([has_endDate, has_endDate_day_precision, has_cycleDuration])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY, by='cycleDuration')
    return should_run


def _run_by_startDate(cycle: dict):
    startDate = cycle.get('startDate')
    is_same_month = startDate[0:7] == cycle.get('endDate', '')[0:7]
    # start of the month if same month as end date
    return f"{startDate}-01" if is_same_month else f"{startDate}-15"


def _should_run_by_startDate(cycle: dict):
    has_startDate = cycle.get('startDate') is not None
    has_month_precision = has_startDate and is_in_months(cycle.get('startDate'))
    no_cycleDuration = cycle.get('cycleDuration') is None

    logRequirements(cycle, model=MODEL, key=MODEL_KEY, by='startDate',
                    has_startDate=has_startDate,
                    has_month_precision=has_month_precision,
                    no_cycleDuration=no_cycleDuration)

    should_run = all([has_startDate, has_month_precision, no_cycleDuration])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY, by='startDate')
    return should_run


def run(cycle: dict):
    return _run_by_cycleDuration(cycle) if _should_run_by_cycleDuration(cycle) else (
        _run_by_startDate(cycle) if _should_run_by_startDate(cycle) else None
    )
