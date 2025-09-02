from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import get_crop_lookup_value
from .utils import run_products_average
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}]
    }
}
LOOKUPS = {
    "crop": "Plantation_density"
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'plantationDensity'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _get_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), default=None)


def run(cycle: dict):
    value = run_products_average(cycle, TERM_ID, _get_value)
    return [_practice(value)] if value is not None else []
