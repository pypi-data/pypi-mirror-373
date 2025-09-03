from hestia_earth.utils.date import is_in_months

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import last_day_of_month
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "month precision",
        "none": {
            "cycleDuration": ""
        }
    }
}
RETURNS = {
    "The endDate as a string": ""
}
MODEL_KEY = 'endDate'


def _end_of_month(date: str):
    year = int(date[0:4])
    month = int(date[5:7])
    return last_day_of_month(year, month).strftime('%Y-%m-%d')


def _run(cycle: dict):
    endDate = cycle.get('endDate')
    is_same_month = endDate[0:7] == cycle.get('startDate', '')[0:7]
    # end of the month if same month as startDate
    return _end_of_month(endDate) if is_same_month else f"{endDate}-14"


def _should_run(cycle: dict):
    has_endDate = cycle.get('endDate') is not None
    has_month_precision = has_endDate and is_in_months(cycle.get('endDate'))
    no_cycleDuration = cycle.get('cycleDuration') is None

    logRequirements(cycle, model=MODEL, key=MODEL_KEY, by='endDate',
                    has_endDate=has_endDate,
                    has_month_precision=has_month_precision,
                    no_cycleDuration=no_cycleDuration)

    should_run = all([has_endDate, has_month_precision, no_cycleDuration])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY, by='endDate')
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
