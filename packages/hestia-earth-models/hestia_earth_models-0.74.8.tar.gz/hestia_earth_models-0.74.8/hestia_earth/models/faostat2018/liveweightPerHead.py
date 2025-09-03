from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import extract_grouped_data_closest_date
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, safe_parse_date, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.term import download_term
from hestia_earth.models.utils.property import _new_property, node_has_no_property
from hestia_earth.models.utils.product import convert_product_to_unit
from hestia_earth.models.utils.animalProduct import FAO_LOOKUP_COLUMN, get_animalProduct_lookup_value
from hestia_earth.models.utils.lookup import get_region_lookup_value
from .utils import get_liveAnimal_to_animalProduct_id
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": ["animalProduct", "liveAnimal"]
        }],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
LOOKUPS = {
    "liveAnimal": ["primaryMeatProductFaoProductionTermId"],
    "animalProduct": ["animalProductGroupingFAOEquivalent", "animalProductGroupingFAO"],
    "region-animalProduct-animalProductGroupingFAO-averageColdCarcassWeight": ""
}
RETURNS = {
    "Product": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'liveweightPerHead'
LOOKUP_WEIGHT = 'region-animalProduct-animalProductGroupingFAO-averageColdCarcassWeight.csv'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _product_value(product: dict, year: int, country_id: str):
    product_id = product.get('term', {}).get('@id')
    groupingFAO = get_animalProduct_lookup_value(MODEL, product_id, FAO_LOOKUP_COLUMN)

    data = get_region_lookup_value(LOOKUP_WEIGHT, country_id, groupingFAO, model=MODEL, term=TERM_ID)
    average_carcass_weight = safe_parse_float(extract_grouped_data_closest_date(data, year), default=None)
    # average_carcass_weight is in hg, divide by 10 to go back to kg
    kg_carcass_weight = average_carcass_weight / 10 if average_carcass_weight else None

    kg_liveweight = convert_product_to_unit({
        **product,
        'value': [kg_carcass_weight]
    }, Units.KG_LIVEWEIGHT) if kg_carcass_weight else None

    return kg_liveweight, groupingFAO


def _should_run_liveAnimal(product: dict):
    return product.get('term', {}).get('termType') == TermTermType.LIVEANIMAL.value


def _run_liveAnimal(cycle: dict, product: dict, year: int, country_id: str):
    # find the animalProduct to get the average carcass weight
    product_id = product.get('term', {}).get('@id')
    animal_product_id = get_liveAnimal_to_animalProduct_id(product_id, LOOKUPS['liveAnimal'][0], term=TERM_ID)

    animal_product_term = download_term(animal_product_id, TermTermType.ANIMALPRODUCT) if animal_product_id else {}
    kg_liveweight, groupingFAO = _product_value({**product, 'term': animal_product_term}, year, country_id)

    logRequirements(cycle, model=MODEL, term=product_id, property=TERM_ID,
                    animal_product_id=animal_product_id,
                    country_id=country_id,
                    year=year,
                    kg_liveweight=kg_liveweight,
                    groupingFAO=groupingFAO)

    should_run = all([kg_liveweight])
    logShouldRun(cycle, MODEL, product_id, should_run, property=TERM_ID)

    return {**product, 'properties': product.get('properties', []) + [_property(kg_liveweight)]} if should_run else None


def _run_animalProduct(cycle: dict, product: dict, year: int, country_id: str):
    product_id = product.get('term', {}).get('@id')
    kg_liveweight, groupingFAO = _product_value(product, year, country_id)

    logRequirements(cycle, model=MODEL, term=product_id, property=TERM_ID,
                    country_id=country_id,
                    year=year,
                    kg_liveweight=kg_liveweight,
                    groupingFAO=groupingFAO)

    should_run = all([kg_liveweight])
    logShouldRun(cycle, MODEL, product_id, should_run, property=TERM_ID)

    return {**product, 'properties': product.get('properties', []) + [_property(kg_liveweight)]} if should_run else None


def run(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None

    products = filter_list_term_type(cycle.get('products', []), [TermTermType.ANIMALPRODUCT, TermTermType.LIVEANIMAL])
    products = list(filter(node_has_no_property(TERM_ID), products))

    return non_empty_list([
        (
            (_run_liveAnimal if _should_run_liveAnimal(p) else _run_animalProduct)(cycle, p, year, country_id)
        ) for p in products
    ]) if country_id else []
