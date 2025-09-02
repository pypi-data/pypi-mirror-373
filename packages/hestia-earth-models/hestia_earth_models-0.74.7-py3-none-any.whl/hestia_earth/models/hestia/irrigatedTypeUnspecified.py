from hestia_earth.schema import CycleFunctionalUnit

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import is_irrigated
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.input import get_total_irrigation_m3
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "functionalUnit": "1 ha",
        "none": {
            "practices": [{"@type": "Practice", "value": "> 0", "term.termType": "waterRegime"}]
        },
        "optional": {
            "inputs": [{"@type": "Input", "term.termType": "water", "value": ""}]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
LOOKUPS = {
    "waterRegime": "irrigated"
}
TERM_ID = 'irrigatedTypeUnspecified'
MIN_IRRIGATION_M3 = 250


def _practice():
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [100]
    return practice


def _should_run(cycle: dict):
    functional_unit = cycle.get('functionalUnit')
    irrigation_value_m3 = get_total_irrigation_m3(cycle)
    is_1_ha_functional_unit = functional_unit == CycleFunctionalUnit._1_HA.value

    no_irrigation_practice = not is_irrigated(cycle, model=MODEL, term=TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    no_irrigation_practice=no_irrigation_practice,
                    is_1_ha_functional_unit=is_1_ha_functional_unit,
                    irrigation_value_m3=irrigation_value_m3,
                    irrigation_min_m3=MIN_IRRIGATION_M3,
                    is_irrigated=irrigation_value_m3 > MIN_IRRIGATION_M3)

    should_run = all([
        no_irrigation_practice,
        is_1_ha_functional_unit,
        irrigation_value_m3 > MIN_IRRIGATION_M3
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict):
    should_run = _should_run(cycle)
    return [_practice()] if should_run else []
