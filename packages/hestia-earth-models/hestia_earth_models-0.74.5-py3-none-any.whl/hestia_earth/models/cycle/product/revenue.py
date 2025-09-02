from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY
from hestia_earth.models.utils.cycle import default_currency
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "optional": {
                "value": "",
                "price": ""
            },
            "none": {
                "revenue": ""
            }
        }]
    }
}
RETURNS = {
    "Product": [{
        "revenue": "",
        "currency": "defaults to USD if multiple currencies are used"
    }]
}
MODEL_KEY = 'revenue'


def _run(cycle: dict):
    currency = default_currency(cycle) or DEFAULT_CURRENCY

    def run(product: dict):
        value = list_sum(product.get('value', [0])) * product.get('price', 0)
        # make sure currency is logged as running
        logShouldRun(cycle, MODEL, product.get('term', {}).get('@id'), True, key='currency')
        return {'currency': currency, **product, MODEL_KEY: value}
    return run


def _should_run(cycle: dict):
    def should_run_product(product: dict):
        term_id = product.get('term', {}).get('@id')

        value = list_sum(product.get('value') or [], default=None)
        has_yield = bool(value)
        is_yield_0 = value == 0

        price = product.get('price') or -1
        has_price = price > 0
        is_price_0 = price == 0

        logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                        has_yield=has_yield,
                        has_price=has_price,
                        is_yield_0=is_yield_0,
                        is_price_0=is_price_0)

        should_run = any([has_yield and has_price, is_yield_0, is_price_0])
        logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run
    return should_run_product


def _should_run_product(product: dict): return product.get(MODEL_KEY) is None


def run(cycle: dict):
    products = list(filter(_should_run_product, cycle.get('products', [])))
    products = list(filter(_should_run(cycle), products))
    return non_empty_list(map(_run(cycle), products))
