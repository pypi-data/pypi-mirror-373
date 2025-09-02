from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logRequirements, logShouldRun
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'


def _run(product: dict):
    value = list_average(product.get('min') + product.get('max'))
    return {**product, MODEL_KEY: [value]}


def _should_run(cycle: dict):
    def should_run_blank_node(product: dict):
        term_id = product.get('term', {}).get('@id')
        value_not_set = len(product.get(MODEL_KEY, [])) == 0
        has_min = len(product.get('min', [])) > 0
        has_max = len(product.get('max', [])) > 0

        should_run = all([value_not_set, has_min, has_max])

        # skip logs if we don't run the model to avoid showing an "error"
        if should_run:
            logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                            value_not_set=value_not_set,
                            has_min=has_min,
                            has_max=has_max)
            logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run

    return should_run_blank_node


def run(cycle: dict):
    products = list(filter(_should_run(cycle), cycle.get('products', [])))
    return non_empty_list(map(_run, products))
