from hestia_earth.schema import TermTermType, CycleStartDateDefinition
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.crop import is_permanent_crop
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "",
        "products": [{
            "@type": "Product",
            "primary": "True",
            "term.termType": "crop"
        }],
        "optional": {
            "endDate": ""
        }
    }
}
RETURNS = {
    "The startDateDefinition as a string": ""
}
MODEL_KEY = 'startDateDefinition'


def _is_last_day_of_month(date: str):
    date_parts = date.split('-')
    return len(date_parts) > 1 and date_parts[1] == '12' and any([
        len(date_parts) == 3 and date_parts[2] == '31',
        len(date_parts) == 2
    ])


def _run(cycle: dict):
    product = find_primary_product(cycle)
    permanent_crop = is_permanent_crop(MODEL, MODEL_KEY, product.get('term', {}))
    return (
        CycleStartDateDefinition.START_OF_YEAR.value if _is_last_day_of_month(cycle.get('endDate'))
        else CycleStartDateDefinition.ONE_YEAR_PRIOR.value
    ) if permanent_crop else (
        CycleStartDateDefinition.HARVEST_OF_PREVIOUS_CROP.value
    )


def _should_run(cycle: dict):
    cycleDuration_added = 'cycleDuration' in cycle.get('added', [])
    product = find_primary_product(cycle) or {}
    product_term_type = product.get('term', {}).get('termType')
    primary_product_is_crop = product_term_type == TermTermType.CROP.value

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    cycleDuration_added=cycleDuration_added,
                    primary_product_is_crop=primary_product_is_crop)

    should_run = all([cycleDuration_added, primary_product_is_crop])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
