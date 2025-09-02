from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "practices": [{"@type": "Practice", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'
LOOKUPS_KEY = 'defaultValue'


def _run(practice: dict):
    value = get_lookup_value(practice.get('term'), LOOKUPS_KEY) or list_average(
        practice.get('min') + practice.get('max')
    )
    return {**practice, MODEL_KEY: [value]}


def _should_run(cycle: dict):
    def should_run_blank_node(practice: dict):
        term_id = practice.get('term', {}).get('@id')
        value_not_set = len(practice.get(MODEL_KEY, [])) == 0
        has_min = len(practice.get('min', [])) > 0
        has_max = len(practice.get('max', [])) > 0
        has_lookup_value = get_lookup_value(practice.get('term'), LOOKUPS_KEY)

        should_run = all([value_not_set, has_lookup_value or all([has_min, has_max])])

        # skip logs if we don't run the model to avoid showing an "error"
        if should_run:
            logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                            value_not_set=value_not_set,
                            has_lookup_value=has_lookup_value,
                            has_min=has_min,
                            has_max=has_max)
            logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run

    return should_run_blank_node


def run(cycle: dict):
    practices = list(filter(_should_run(cycle), cycle.get('practices', [])))
    return non_empty_list(map(_run, practices))
