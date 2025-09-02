from functools import reduce
from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, flatten, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _omit, _include
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.blank_node import condense_nodes
from hestia_earth.models.utils.crop import get_landCover_term_id
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [
            {
                "@type": "Product",
                "term.termType": ["crop", "forage"],
                "optional": {
                    "startDate": "",
                    "endDate": ""
                }
            }
        ],
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        },
        "none": {
            "practices": [{"@type": "Practice", "term.termType": "landCover"}]
        },
        "optional": {
            "startDate": ""
        }
    }
}
RETURNS = {
    "Practice": [{
        "term.termType": "landCover",
        "value": "",
        "endDate": "",
        "startDate": ""
    }]
}
LOOKUPS = {
    "crop": ["landCoverTermId", "maximumCycleDuration"],
    "forage": ["landCoverTermId"],
    "property": ["GAP_FILL_TO_MANAGEMENT", "CALCULATE_TOTAL_LAND_COVER_SHARE_SEPARATELY"]
}
MODEL_KEY = 'landCover'


def practice(data: dict):
    node = _new_practice(data.get('id'))
    node['value'] = [data['value']]
    node['endDate'] = data['endDate']
    if data.get('startDate'):
        node['startDate'] = data['startDate']
    if data.get('properties'):
        node['properties'] = data['properties']
    return node


def _should_gap_fill(term: dict):
    value = get_lookup_value(lookup_term=term, column='GAP_FILL_TO_MANAGEMENT')
    return bool(value)


def _filter_properties(blank_node: dict):
    properties = list(filter(lambda p: _should_gap_fill(p.get('term', {})), blank_node.get('properties', [])))
    return _omit(blank_node, ['properties']) | ({'properties': properties} if properties else {})


def _map_to_value(value: dict):
    return {
        'id': value.get('term', {}).get('@id'),
        'value': value.get('value'),
        'startDate': value.get('startDate'),
        'endDate': value.get('endDate'),
        'properties': value.get('properties')
    }


def _copy_item_if_exists(source: dict, keys: list[str] = None, dest: dict = None) -> dict:
    return reduce(lambda p, c: p | ({c: source[c]} if source.get(c) else {}), keys or [], dest or {})


def _run(cycle: dict, products: list, total: float):
    # remove any properties that should not get gap-filled
    products = list(map(_filter_properties, products))

    nodes = [
        _map_to_value(_include(cycle, ["startDate", "endDate"]) | _copy_item_if_exists(
            source=product,
            keys=['properties', 'startDate', 'endDate'],
            dest={
                "term": {'@id': product.get('land-cover-id')},
                "value": round((100 - total) / len(products), 2)
            }
        ))
        for product in products
    ]

    return condense_nodes(list(map(practice, nodes)))


def _should_group_landCover(term: dict):
    value = get_lookup_value(lookup_term=term, column='CALCULATE_TOTAL_LAND_COVER_SHARE_SEPARATELY')
    return bool(value)


def _has_prop_grouped_with_landCover(product: dict):
    return bool(
        next((
            p
            for p in product.get('properties', [])
            if _should_group_landCover(p.get('term', {}))
        ), None)
    )


def _product_wit_landCover_id(product: dict):
    landCover_id = get_landCover_term_id(product.get('term', {}))
    return product | {'land-cover-id': landCover_id} if landCover_id else None


def _should_run(cycle: dict):
    is_cropland = cycle.get('site', {}).get('siteType') == SiteSiteType.CROPLAND.value

    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.LANDCOVER)
    # split practices with properties that group with landCover
    practices_max_100 = [
        p for p in practices if _has_prop_grouped_with_landCover(p)
    ]
    total_practices_max_100 = list_sum([
        list_sum(p.get('value', []))
        for p in practices_max_100
    ])
    practices_without_grouped_props = [
        p for p in practices if not _has_prop_grouped_with_landCover(p)
    ]

    products = filter_list_term_type(cycle.get('products', []), [TermTermType.CROP, TermTermType.FORAGE])
    # only take products with a matching landCover term
    products = non_empty_list(map(_product_wit_landCover_id, products))

    # Products that can sum up to 100% => run if total is below 100%
    products_max_100 = [
        p for p in products
        if _has_prop_grouped_with_landCover(p)
    ] if total_practices_max_100 < 100 else []

    # Products that must sum up to 100% => can not run practices already exist as already 100%
    products_is_100 = [
        p for p in products
        if not _has_prop_grouped_with_landCover(p)
    ] if not practices_without_grouped_props else []

    has_crop_forage_products = bool(products_max_100 + products_is_100)

    logRequirements(cycle, model=MODEL, model_key=MODEL_KEY,
                    is_cropland=is_cropland,
                    has_crop_forage_products=has_crop_forage_products)

    should_run = all([is_cropland, has_crop_forage_products])
    logShouldRun(cycle, MODEL, None, should_run, model_key=MODEL_KEY)

    return should_run, [
        (products_max_100, total_practices_max_100),
        (products_is_100, 0)
    ]


def run(cycle: dict):
    should_run, products_list = _should_run(cycle)
    return flatten([
        _run(cycle, products, total)
        for products, total in products_list if products
    ]) if should_run else []
