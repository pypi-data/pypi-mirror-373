from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property, get_node_property, node_has_no_property
from hestia_earth.models.utils.term import get_lookup_value
from .utils import get_yield_dm
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [
            {
                "@type": "Product",
                "term.termType": "cropResidue"
            },
            {
                "@type": "Product",
                "term.termType": ["crop", "forage"],
                "value": "> 0",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "dryMatter"}]
                }
            }
        ]
    }
}
LOOKUPS = {
    "crop": [
        "IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes",
        "C_CONTENT_AG_CROP_RESIDUE", "C_CONTENT_BG_CROP_RESIDUE"
    ],
    "forage": [
        "IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes",
        "C_CONTENT_AG_CROP_RESIDUE", "C_CONTENT_BG_CROP_RESIDUE"
    ]
}
RETURNS = {
    "Product": [{
        "properties": [{
            "@type": "Property",
            "value": "",
            "term.@id": "carbonContent"
        }]
    }]
}
TERM_ID = 'carbonContent'
PROPERTY_KEY = 'dryMatter'
LOOKUPS = [
    'C_CONTENT_AG_CROP_RESIDUE',
    'C_CONTENT_BG_CROP_RESIDUE'
]


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _crop_residue_lookup_col(term):
    term_id = term.get('@id') if isinstance(term, dict) else term
    return LOOKUPS[0] if term_id.startswith('above') else (
        LOOKUPS[1] if term_id.startswith('below') else None
    )


def _get_lookup_value(term: dict, column: str):
    return safe_parse_float(get_lookup_value(term, column, model=MODEL, term=TERM_ID), default=None)


# Single crop


def _get_single_product_value(term: dict, product_id: str):
    column = _crop_residue_lookup_col(product_id)
    return _get_lookup_value(term, column) if column else None


def _run_single_product(crop_residue_products: list, primary_product: dict):
    primary_product_term = primary_product.get('term', {})

    def run_product(product: dict):
        term_id = product.get('term', {}).get('@id')
        value = _get_single_product_value(primary_product_term, term_id)
        prop = _property(value) if value is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else product

    return non_empty_list(map(run_product, crop_residue_products))


def _should_run_single_product(product: dict):
    term = product.get('term', {})
    term_id = term.get('@id')
    has_single_values = any(_get_lookup_value(term, column) for column in LOOKUPS)

    debugValues(product, model=MODEL, term=term_id, property=TERM_ID,
                has_single_values=has_single_values)

    return all([has_single_values])


# Multiple crops


def _multiple_product_values(crop: dict, residue_id: str):
    term = crop.get('term', {})
    term_id = term.get('@id')
    value = list_sum(crop.get('value'))
    dm = get_node_property(crop, PROPERTY_KEY).get('value', 0)
    # IPCC_2019_Ratio_AGRes_YieldDM
    yield_dm = get_yield_dm(TERM_ID, term) or 0
    # LIGNIN_CONTENT_AG_CROP_RESIDUE or LIGNIN_CONTENT_BG_CROP_RESIDUE
    c_content = _get_lookup_value(term, _crop_residue_lookup_col(residue_id))
    ratio = _get_lookup_value(term, 'IPCC_2019_Ratio_BGRes_AGRes') if residue_id == 'belowGroundCropResidue' else 1
    debugValues(crop, model=MODEL, term=residue_id, property=TERM_ID,
                crop=term_id,
                dryMatter=dm,
                ratio_yield_dm=yield_dm,
                carbonContent=c_content,
                ratio=ratio)
    return (value * dm / 100 * yield_dm * (ratio or 1), c_content) if c_content is not None else None


def _run_multiple_products(crop_residue_products: list, products: list):
    def run_product(product: dict):
        term_id = product.get('term', {}).get('@id')
        values = non_empty_list([_multiple_product_values(p, term_id) for p in products])
        total = sum([value for value, _ in values])
        value = sum([value * c_content for value, c_content in values]) / total if total > 0 else None
        prop = _property(value) if value is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None

    return non_empty_list(map(run_product, crop_residue_products))


def _should_run_multiple_products(product: dict):
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value', [0]))
    prop = get_node_property(product, PROPERTY_KEY).get('value')
    yield_dm = _get_lookup_value(product.get('term', {}), 'IPCC_2019_Ratio_AGRes_YieldDM')

    debugValues(product, model=MODEL, term=term_id, property=TERM_ID,
                dryMatter=prop,
                yield_dm=yield_dm)

    return all([value > 0, prop, yield_dm is not None])


def _should_run_product(product: dict):
    return _crop_residue_lookup_col(product.get('term', {})) is not None


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROPRESIDUE)
    products = list(filter(node_has_no_property(TERM_ID), products))
    crop_residue_products = list(filter(_should_run_product, products))

    has_crop_residue_products = len(crop_residue_products) > 0

    crop_forage_products = filter_list_term_type(cycle.get('products', []), [TermTermType.CROP, TermTermType.FORAGE])

    single_products = list(filter(_should_run_single_product, crop_forage_products))
    single_product = single_products[0] if len(single_products) == 1 else None
    has_single_crop_forage = single_product is not None

    multiple_products = list(filter(_should_run_multiple_products, crop_forage_products))
    has_multiple_crops_forages = len(multiple_products) > 1

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_crop_residue_products=has_crop_residue_products)

    should_run = all([has_crop_residue_products, has_single_crop_forage or has_multiple_crops_forages])

    for product in crop_residue_products:
        term_id = product.get('term', {}).get('@id')
        logRequirements(cycle, model=MODEL, term=term_id, property=TERM_ID,
                        has_single_crop_forage=has_single_crop_forage,
                        has_multiple_crops_forages=has_multiple_crops_forages)
        logShouldRun(cycle, MODEL, term_id, should_run, property=TERM_ID)

    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, crop_residue_products, single_product, multiple_products


def run(cycle: dict):
    should_run, crop_residue_products, single_product, multiple_products = _should_run(cycle)
    return (
        _run_single_product(crop_residue_products, single_product) if single_product else
        _run_multiple_products(crop_residue_products, multiple_products)
    ) if should_run else []
