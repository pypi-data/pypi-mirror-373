from hestia_earth.schema import TermTermType, CycleStartDateDefinition
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.crop import is_permanent_crop
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "> 0",
        "none": {
            "otherSites": [{"@type": "Site"}]
        },
        "optional": {
            "products": [{
                "@type": "Product",
                "primary": "True",
                "term.termType": "crop"
            }],
            "startDateDefinition": ""
        }
    }
}
RETURNS = {
    "the duration as a `number`": ""
}
MODEL_KEY = 'siteDuration'


def _run(cycle: dict): return cycle.get('cycleDuration')


def _should_run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 0)
    has_single_site = len(cycle.get('otherSites', [])) == 0

    product = find_primary_product(cycle)
    product_term = (product or {}).get('term', {})
    is_primary_crop_product = product_term.get('termType') == TermTermType.CROP.value
    permanent_crop = is_permanent_crop(MODEL, MODEL_KEY, product_term)
    harvest_previous_crop = CycleStartDateDefinition.HARVEST_OF_PREVIOUS_CROP.value
    is_harvest_previous_crop = cycle.get('startDateDefinition') == harvest_previous_crop

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    cycleDuration=cycleDuration,
                    has_single_site=has_single_site,
                    is_primary_crop_product=is_primary_crop_product,
                    is_permanent_crop=permanent_crop,
                    is_harvest_previous_crop=is_harvest_previous_crop)

    should_run = all([
        cycleDuration > 0,
        has_single_site,
        not is_primary_crop_product or permanent_crop or is_harvest_previous_crop
    ])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
