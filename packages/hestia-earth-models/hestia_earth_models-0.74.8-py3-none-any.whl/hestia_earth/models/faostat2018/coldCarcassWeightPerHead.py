from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.property import _new_property, node_has_no_property
from . import MODEL
from .utils import product_equivalent_value

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [
            {"@type": "Product", "value": "", "term.termType": "animalProduct", "term.units": "kg cold carcass weight"}
        ],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
LOOKUPS = {
    "region-animalProduct-animalProductGroupingFAO-productionQuantity": "",
    "region-animalProduct-animalProductGroupingFAO-head": ""
}
RETURNS = {
    "Product": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'coldCarcassWeightPerHead'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _should_run_product(cycle: dict, year: int, country: str):
    def exec(product: dict):
        product_id = product.get('term', {}).get('@id')
        value = product_equivalent_value(product, year, country)
        should_run = all([value])
        logShouldRun(cycle, MODEL, product_id, should_run, property=TERM_ID)
        return should_run, product, value
    return exec


def _run(products: list):
    def run_product(values: tuple):
        product, value = values
        prop = _property(value)
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    products = _filter_list_term_unit(products, Units.KG_COLD_CARCASS_WEIGHT)
    products = list(filter(node_has_no_property(TERM_ID), products))
    has_kg_carcass_products = len(products) > 0

    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None
    country = cycle.get('site', {}).get('country', {}).get('@id')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_kg_carcass_products=has_kg_carcass_products,
                    year=year,
                    country=country)

    should_run = all([has_kg_carcass_products, year, country])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products, year, country


def run(cycle: dict):
    should_run, products, year, country = _should_run(cycle)
    products = list(map(_should_run_product(cycle, year, country), products)) if should_run else []
    products = [(product, value) for (should_run, product, value) in products if should_run]
    return _run(products) if should_run else []
