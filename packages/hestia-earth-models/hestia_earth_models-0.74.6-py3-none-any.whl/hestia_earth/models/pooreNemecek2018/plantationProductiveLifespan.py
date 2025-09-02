from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugValues, log_as_table
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import get_crop_lookup_value
from .utils import run_products_average
from .plantationLifespan import _get_value as get_plantationLifespan
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}]
    }
}
LOOKUPS = {
    "crop": "Plantation_non-productive_lifespan"
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'plantationProductiveLifespan'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _get_value(cycle: dict):
    def get(product: dict):
        term_id = product.get('term', {}).get('@id', '')
        plantationLifespan = get_plantationLifespan(product)
        nonProductiveLifespan = safe_parse_float(
            get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), default=None
        )
        product_id = product.get('term').get('@id')
        product_id_logs = log_as_table({
            'plantationLifespan': plantationLifespan,
            'nonProductiveLifespan': nonProductiveLifespan
        })
        debugValues(cycle, model=MODEL, term=TERM_ID,
                    **{product_id: product_id_logs})
        return plantationLifespan - nonProductiveLifespan if all([
            plantationLifespan is not None, nonProductiveLifespan is not None
         ]) else None
    return get


def run(cycle: dict):
    value = run_products_average(cycle, TERM_ID, _get_value(cycle))
    return [_practice(value)] if value is not None else []
