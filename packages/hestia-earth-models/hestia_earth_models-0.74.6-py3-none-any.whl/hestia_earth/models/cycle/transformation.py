from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "optional": {
            "transformations": [
                {"@type": "Transformation", "inputs": [{"@type": "Input", "value": ""}]}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": ""
    }]
}
MODEL_KEY = 'transformation'
MODEL_LOG = '/'.join([MODEL, MODEL_KEY])


def _run_emission(cycle: dict, transformation: dict):
    def exec(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        logShouldRun(cycle, MODEL_LOG, term_id, True, key=MODEL_KEY)
        return emission | {MODEL_KEY: transformation.get('term', {})}
    return exec


def _emissions(cycle: dict):
    def exec(transformation: dict):
        emissions = transformation.get('emissions', [])
        should_run = len(transformation.get('inputs', [])) > 0
        return list(map(_run_emission(cycle, transformation), emissions)) if should_run else []
    return exec


def run(cycle: dict): return flatten(list(map(_emissions(cycle), cycle.get('transformations', []))))
