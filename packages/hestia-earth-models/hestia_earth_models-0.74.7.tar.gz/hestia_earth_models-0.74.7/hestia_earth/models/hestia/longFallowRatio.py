from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "practices": [
            {"@type": "Practice", "value": "> 0", "term.@id": "longFallowDuration"},
            {"@type": "Practice", "value": "> 0", "term.@id": "rotationDuration"}
        ]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'longFallowRatio'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [round(value, 7)]
    return practice


def _run(longFallowDuration: float, rotationDuration: float):
    value = rotationDuration / (rotationDuration - longFallowDuration)
    return [_practice(value)]


def _should_run(cycle: dict):
    practices = cycle.get('practices', [])

    longFallowDuration = list_sum(find_term_match(practices, 'longFallowDuration', {}).get('value', 0), 0)
    rotationDuration = list_sum(find_term_match(practices, 'rotationDuration', {}).get('value', 0), 0)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    longFallowDuration=longFallowDuration,
                    rotationDuration=rotationDuration)

    should_run = all([longFallowDuration > 0, rotationDuration > 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, longFallowDuration, rotationDuration


def run(cycle: dict):
    should_run, longFallowDuration, rotationDuration = _should_run(cycle)
    return _run(longFallowDuration, rotationDuration) if should_run else []
