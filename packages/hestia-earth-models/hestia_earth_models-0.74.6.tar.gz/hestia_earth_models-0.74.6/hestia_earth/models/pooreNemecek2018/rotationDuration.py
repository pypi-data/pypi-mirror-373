from hestia_earth.models.log import debugValues, log_as_table
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils import sum_values
from .plantationLifespan import _get_value as get_plantationLifespan
from .longFallowDuration import _get_value as get_longFallowDuration
from .utils import run_products_average
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}]
    }
}
LOOKUPS = {
    "crop": ["Plantation_lifespan", "Plantation_longFallowDuration"]
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'rotationDuration'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _get_value(cycle: dict):
    def get(product: dict):
        plantationLifespan = get_plantationLifespan(product)
        longFallowDuration = get_longFallowDuration(product)
        product_id = product.get('term').get('@id')
        product_id_logs = log_as_table({
            'plantationLifespan': plantationLifespan,
            'longFallowDuration': longFallowDuration
        })
        debugValues(cycle, model=MODEL, term=TERM_ID,
                    **{product_id: product_id_logs})
        return sum_values([plantationLifespan, longFallowDuration])
    return get


def run(cycle: dict):
    value = run_products_average(cycle, TERM_ID, _get_value(cycle))
    return [_practice(value)] if value is not None else []
