from .utils import _should_run, _practice

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False"
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'residueLeftOnField'


def run(cycle: dict):
    should_run, remaining_value, *args = _should_run(TERM_ID, cycle)
    return [_practice(TERM_ID, remaining_value)] if should_run else []
