from hestia_earth.schema import CycleStartDateDefinition
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import is_plantation
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "> 0",
        "startDateDefinition": "harvest of previous crop"
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
LOOKUPS = {
    "crop": "isPlantation"
}
TERM_ID = 'croppingIntensity'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [round(value, 7)]
    return practice


def _run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration')
    return [_practice(cycleDuration / 365)]


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    not_plantation = not is_plantation(MODEL, TERM_ID, product.get('term', {}).get('@id'))

    cycleDuration = cycle.get('cycleDuration', 0)
    has_cycleDuration = cycleDuration > 0
    startDateDefinition = cycle.get('startDateDefinition')
    harvest_previous_crop = CycleStartDateDefinition.HARVEST_OF_PREVIOUS_CROP.value
    is_harvest_previous_crop = startDateDefinition == harvest_previous_crop

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    not_plantation=not_plantation,
                    cycleDuration=cycleDuration,
                    is_harvest_previous_crop=is_harvest_previous_crop)

    should_run = all([not_plantation, has_cycleDuration, is_harvest_previous_crop])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
