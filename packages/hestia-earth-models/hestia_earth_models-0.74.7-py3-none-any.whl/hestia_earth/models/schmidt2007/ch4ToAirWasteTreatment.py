from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from .utils import get_waste_values
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": ""}]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "waste": "ch4EfSchmidt2007"
}
TERM_ID = 'ch4ToAirWasteTreatment'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(waste_values: list):
    value = list_sum(waste_values)
    return [_emission(value)]


def _should_run(cycle: dict):
    waste_values = get_waste_values(TERM_ID, cycle, LOOKUPS['waste'])
    has_waste = len(waste_values) > 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_waste=has_waste)

    should_run = any([has_waste])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, waste_values


def run(cycle: dict):
    should_run, waste_values = _should_run(cycle)
    return _run(waste_values) if should_run else []
