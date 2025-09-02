from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logShouldRun, logRequirements
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{"@type": "Input", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Input": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'


def _run(input: dict):
    value = list_average(input.get('min') + input.get('max'))
    return {**input, MODEL_KEY: [value]}


def _should_run(cycle: dict):
    def should_run_input(input: dict):
        term_id = input.get('term', {}).get('@id')
        value_not_set = len(input.get(MODEL_KEY, [])) == 0
        has_min = len(input.get('min', [])) > 0
        has_max = len(input.get('max', [])) > 0

        should_run = all([value_not_set, has_min, has_max])

        # skip logs if we don't run the model to avoid showing an "error"
        if should_run:
            logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                            value_not_set=value_not_set,
                            has_min=has_min,
                            has_max=has_max)
            logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run

    return should_run_input


def run(cycle: dict):
    inputs = list(filter(_should_run(cycle), cycle.get('inputs', [])))
    return non_empty_list(map(_run, inputs))
