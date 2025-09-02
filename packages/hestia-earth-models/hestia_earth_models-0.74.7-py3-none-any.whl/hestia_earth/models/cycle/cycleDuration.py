from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match, find_primary_product
from hestia_earth.utils.date import diff_in_days

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils.crop import is_permanent_crop
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "optional": {
            "startDate": "",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "term.termType": "crop"
            }],
            "practices": [{"@type": "Practice", "value": "", "term.@id": "croppingIntensity"}]
        }
    }
}
RETURNS = {
    "a `number` or `None` if requirements are not met": ""
}
LOOKUPS = {
    "crop": "cropGroupingFAO"
}
MODEL_KEY = 'cycleDuration'
DEFAULT_DURATION = 365


def _run_by_dates(cycle: dict):
    start_date = cycle.get('startDate')
    end_date = cycle.get('endDate')
    return diff_in_days(start_date, end_date)


def _should_run_by_dates(cycle: dict):
    start_date = cycle.get('startDate', '')
    start_date_has_day = len(start_date) == 10
    end_date = cycle.get('endDate', '')
    end_date_has_day = len(start_date) == 10

    logRequirements(cycle, model=MODEL, key=MODEL_KEY, by='dates',
                    start_date_has_day=start_date_has_day,
                    start_date=start_date,
                    end_date_has_day=end_date_has_day,
                    end_date=end_date)

    should_run = all([start_date_has_day, end_date_has_day])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY, by='dates')
    return should_run


def _run_by_crop(cycle: dict):
    product = find_primary_product(cycle)
    permanent_crop = is_permanent_crop(MODEL, MODEL_KEY, product.get('term', {}))
    croppingIntensity = find_term_match(cycle.get('practices', []), 'croppingIntensity').get('value', [1])[0]
    ratio = 1 if permanent_crop else croppingIntensity
    debugValues(cycle, model=MODEL, key=MODEL_KEY, by='product',
                is_permanent_crop=permanent_crop,
                croppingIntensity=croppingIntensity,
                ratio=ratio)
    return round(DEFAULT_DURATION * ratio, 3)


def _should_run_by_crop(cycle: dict):
    product = find_primary_product(cycle) or {}
    product_term_type = product.get('term', {}).get('termType')
    primary_product_is_crop = product_term_type == TermTermType.CROP.value

    logRequirements(cycle, model=MODEL, key=MODEL_KEY, by='product',
                    primary_product_is_crop=primary_product_is_crop)

    should_run = all([primary_product_is_crop])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY, by='product')
    return should_run


def run(cycle: dict):
    return _run_by_dates(cycle) if _should_run_by_dates(cycle) else (
        _run_by_crop(cycle) if _should_run_by_crop(cycle)
        else None
    )
