from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY, convert
from .. import MODEL
from .revenue import _run as run_revenue

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [{"@type": "Product", "price": "", "currency": "not in USD"}]
    }
}
RETURNS = {
    "Product": [{
        "currency": "USD",
        "price": "in USD",
        "revenue": "in USD"
    }]
}
MODEL_KEY = 'currency'


def _run_with_revenue(cycle: dict, product: dict, price: float):
    logShouldRun(cycle, MODEL, product.get('term', {}).get('@id'), True, key='revenue')
    logShouldRun(cycle, MODEL, product.get('term', {}).get('@id'), True, key='price')
    return run_revenue(cycle)({**product, 'currency': DEFAULT_CURRENCY, 'price': price})


def _run_product(cycle: dict):
    date = cycle.get('endDate')

    def run(product: dict):
        price = convert(product.get('price'), product.get('currency'), date)
        return None if price is None else _run_with_revenue(cycle, product, price)
    return run


def _product_currency_not_default(product: dict): return product.get('currency', '') != DEFAULT_CURRENCY


def _should_run_product(cycle: dict):
    def should_run_product(product: dict):
        term_id = product.get('term', {}).get('@id')
        price = product.get('price')
        has_price = price is not None

        logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                        has_price=has_price)

        should_run = all([has_price])
        logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
        return should_run
    return should_run_product


def run(cycle: dict):
    # make sure we only run on product which currency is NOT the default value
    products = list(filter(_product_currency_not_default, cycle.get('products', [])))
    products = list(filter(_should_run_product(cycle), products))
    return non_empty_list(map(_run_product(cycle), products))
