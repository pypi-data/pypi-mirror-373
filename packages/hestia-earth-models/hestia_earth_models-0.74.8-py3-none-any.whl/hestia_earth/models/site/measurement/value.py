from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logRequirements, logShouldRun
from .. import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [{"@type": "Measurement", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Measurement": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'


def _run(measurement: dict):
    value = list_average(measurement.get('min') + measurement.get('max'))
    return {**measurement, MODEL_KEY: [value]}


def _should_run(site: dict):
    def should_run_blank_node(measurement: dict):
        term_id = measurement.get('term', {}).get('@id')
        value_not_set = len(measurement.get(MODEL_KEY, [])) == 0
        has_min = len(measurement.get('min', [])) > 0
        has_max = len(measurement.get('max', [])) > 0

        should_run = all([value_not_set, has_min, has_max])

        # skip logs if we don't run the model to avoid showing an "error"
        if should_run:
            logRequirements(site, model=MODEL, term=term_id, key=MODEL_KEY,
                            value_not_set=value_not_set,
                            has_min=has_min,
                            has_max=has_max)
            logShouldRun(site, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run

    return should_run_blank_node


def run(site: dict):
    measurements = list(filter(_should_run(site), site.get('measurements', [])))
    return non_empty_list(map(_run, measurements))
