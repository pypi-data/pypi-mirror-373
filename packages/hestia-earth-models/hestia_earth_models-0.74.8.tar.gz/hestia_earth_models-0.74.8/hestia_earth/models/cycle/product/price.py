from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY
from .utils import lookup_share
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "optional": {
                "revenue": "0"
            },
            "none": {
                "price": ""
            }
        }]
    }
}
RETURNS = {
    "Product": [{
        "price": ""
    }]
}
LOOKUPS = {
    "@doc": "Depending on the primary product [termType](https://hestia.earth/schema/Product#term)",
    "crop": "global_economic_value_share",
    "processedFood": "global_economic_value_share",
    "excreta": "global_economic_value_share",
    "animalProduct": "global_economic_value_share",
    "waste": "global_economic_value_share"
}
MODEL_KEY = 'price'


def _product(product: dict, value: float):
    # currency is required, but do not override if present
    # currency in lookup table is set to USD
    return {'currency': DEFAULT_CURRENCY, **product, MODEL_KEY: value}


def _should_run_product(cycle: dict, product: dict):
    term_id = product.get('term', {}).get('@id')

    value = list_sum(product.get('value') or [], default=None)
    is_yield_0 = value == 0

    share = lookup_share(MODEL_KEY, product)
    share_is_0 = share is not None and share == 0

    revenue = product.get('revenue', -1)
    revenue_is_0 = revenue == 0

    logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY, by='economicValueShare',
                    global_economic_value_share=share,
                    share_is_0=share_is_0,
                    revenue=revenue,
                    revenue_is_0=revenue_is_0,
                    product_yield=value,
                    is_yield_0=is_yield_0)

    should_run = any([share_is_0, revenue_is_0, is_yield_0])
    logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY, by='economicValueShare')
    return should_run


def run(cycle: dict):
    products = list(filter(lambda p: p.get(MODEL_KEY) is None, cycle.get('products', [])))
    return non_empty_list([
        (
            _product(p, 0) if _should_run_product(cycle, p) else None
        ) for p in products
    ])
