from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.property import (
    _new_property, node_has_property, node_has_no_property, get_node_property_value
)
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "animalProduct",
            "term.units": "kg cold carcass weight",
            "properties": [
                {"@type": "Property", "value": "", "term.@id": "liveweightPerHead"},
                {"@type": "Property", "value": "", "term.@id": "processingConversionLiveweightToReadyToCookWeight"}
            ]
        }]
    }
}
RETURNS = {
    "Product": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'readyToCookWeightPerHead'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _run(product: dict):
    liveweightPerHead = get_node_property_value(MODEL, product, 'liveweightPerHead', term=TERM_ID)
    processingConversion = get_node_property_value(
        MODEL, product, 'processingConversionLiveweightToReadyToCookWeight', term=TERM_ID
    )
    value = liveweightPerHead * processingConversion if all([liveweightPerHead, processingConversion]) else None
    prop = _property(value) if value else None
    return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None


def _should_run_product(cycle):
    def exec(product: dict):
        product_id = product.get('term', {}).get('@id')
        should_run = all([
            node_has_no_property(TERM_ID)(product),
            node_has_property('liveweightPerHead')(product),
            node_has_property('processingConversionLiveweightToReadyToCookWeight')(product)
        ])
        logShouldRun(cycle, MODEL, product_id, should_run, property=TERM_ID)
        return should_run
    return exec


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    products = _filter_list_term_unit(products, Units.KG_COLD_CARCASS_WEIGHT)
    products = list(filter(_should_run_product(cycle), products))
    has_matching_products = len(products) > 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_matching_products=has_matching_products)

    should_run = all([has_matching_products])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return non_empty_list(map(_run, products)) if should_run else []
