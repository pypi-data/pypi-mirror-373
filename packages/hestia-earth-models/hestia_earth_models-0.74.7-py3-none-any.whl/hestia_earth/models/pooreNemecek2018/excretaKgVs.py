from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.model import find_primary_product, find_term_match, filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import get_kg_VS_term_id, _filter_list_term_unit, _omit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.input import get_feed_inputs
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.blank_node import convert_to_carbon
from .utils import get_excreta_product_with_ratio
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.product": "True",
        "products": [{
            "@type": "Product",
            "primary": "True",
            "value": "",
            "term.termType": ["animalProduct", "liveAnimal", "liveAquaticSpecies"]
        }],
        "or": [
            {
                "products": [{
                    "@type": "Product",
                    "primary": "True",
                    "value": "",
                    "properties": [{"@type": "Property", "value": "", "term.@id": "carbonContent"}]
                }],
                "practices": [
                    {"@type": "Practice", "value": "", "term.@id": "slaughterAge"},
                    {"@type": "Practice", "value": "", "term.@id": "yieldOfPrimaryAquacultureProductLiveweightPerM2"}
                ],
                "site": {
                    "@type": "Site",
                    "measurements": [{"@type": "Measurement", "value": "", "term.@id": "netPrimaryProduction"}]
                },
                "or": [
                    {
                        "animals": [{
                            "@type": "Animal",
                            "inputs": [{
                                "@type": "Input",
                                "term.units": "kg",
                                "value": "> 0",
                                "properties": [
                                    {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"},
                                    {"@type": "Property", "value": "", "term.@id": "carbonContent"}
                                ]
                            }]
                        }]
                    },
                    {
                        "inputs": [{
                            "@type": "Input",
                            "term.units": "kg",
                            "value": "> 0",
                            "isAnimalFeed": "True",
                            "properties": [
                                {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"},
                                {"@type": "Property", "value": "", "term.@id": "carbonContent"}
                            ]
                        }]
                    }
                ],
                "optional": {
                    "practices": [{"@type": "Practice", "term.termType": "system"}]
                }
            },
            {
                "products": [{
                    "@type": "Product",
                    "term.termType": "excreta",
                    "term.units": "kg N",
                    "value": "",
                    "properties": [{"@type": "Property", "value": "", "term.@id": "volatileSolidsContent"}]
                }]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
LOOKUPS = {
    "crop-property": ["carbonContent", "energyContentHigherHeatingValue"],
    "animalProduct": ["excretaKgVsTermIds"],
    "liveAnimal": ["excretaKgVsTermIds"],
    "liveAquaticSpecies": ["excretaKgVsTermIds"]
}
MODEL_KEY = 'excretaKgVs'

Conv_AQ_CLW_CO2CR = 1
Conv_AQ_CLW_CExcr = 0.5
Conv_AQ_OC_OCSed_Marine = 0.55
Conv_AQ_OC_OCSed_Fresh = 0.35


def _product(excreta_product: str, value: float = None):
    product = _new_product(excreta_product.get('term', {}).get('@id'), value, MODEL)
    return _omit(excreta_product, ['value']) | product


def _run_no_value(excreta_vs_products: list, excreta_n_products: list):
    return [_product(excreta_product) for excreta_product in (excreta_n_products or excreta_vs_products)]


def _run(excreta_vs_products: list, excreta_n_products: list, mass_balance_items: list, inputs_c: float):
    carbonContent, yield_per_m2, slaughterAge, aqocsed, npp = mass_balance_items
    value = max(
        inputs_c + (npp * slaughterAge) / (yield_per_m2 * 1000) - carbonContent - carbonContent * Conv_AQ_CLW_CO2CR,
        carbonContent * Conv_AQ_CLW_CExcr
    ) * aqocsed if all(mass_balance_items) else 0
    return [
        _product(excreta_product, excreta_product.get('value'))
        for excreta_product in excreta_n_products
    ] if excreta_n_products else [
        # ratio is stored in product value
        _product(excreta_product, round(value * excreta_product.get('value')[0] / 100, 7))
        for excreta_product in excreta_vs_products
    ] if value > 0 else []


def _get_carbonContent(cycle: dict):
    primary_prod = find_primary_product(cycle) or {}
    return safe_parse_float(
        get_lookup_value(primary_prod.get('term', {}), 'carbonContent', model=MODEL, model_key=MODEL_KEY), default=0
    ) / 100


def _get_conv_aq_ocsed(siteType: str):
    return Conv_AQ_OC_OCSed_Marine if siteType == SiteSiteType.SEA_OR_OCEAN.value else Conv_AQ_OC_OCSed_Fresh


def _should_run(cycle: dict):
    excreta_vs_products = get_excreta_product_with_ratio(cycle, 'excretaKgVsTermIds', model_key=MODEL_KEY)
    first_term_id = excreta_vs_products[0].get('term', {}).get('@id') if excreta_vs_products else None

    dc = cycle.get('completeness', {})
    is_animalFeed_complete = dc.get('animalFeed', False)
    is_product_complete = dc.get('product', False)

    carbonContent = _get_carbonContent(cycle)

    inputs_feed = get_feed_inputs(cycle)
    inputs_c = convert_to_carbon(cycle, MODEL, inputs_feed, term=first_term_id, model_key=MODEL_KEY)

    practices = cycle.get('practices', [])
    yield_per_m2 = list_sum(
        find_term_match(practices, 'yieldOfPrimaryAquacultureProductLiveweightPerM2').get('value', []), default=None
    )
    slaughterAge = list_sum(find_term_match(practices, 'slaughterAge').get('value', []), default=None)

    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    aqocsed = _get_conv_aq_ocsed(site.get('siteType', {}))
    npp = most_relevant_measurement_value(site.get('measurements', []), 'netPrimaryProduction', end_date)

    # we can still run the model with excreta in "kg N" units
    excreta_products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    default_using_kg_N = not any([
        find_term_match(excreta_products, product.get('term', {}).get('@id'))
        for product in excreta_vs_products
    ])
    excreta_n_products = _filter_list_term_unit(excreta_products, Units.KG_N) if default_using_kg_N else []
    excreta_n_products = [
        (
            excreta_n_product,
            get_node_property(excreta_n_product, 'volatileSolidsContent').get('value', 0)
        )
        for excreta_n_product in excreta_n_products
    ]
    excreta_n_products = [
        {
            'term': {'@id': get_kg_VS_term_id(excreta_n_product.get('term', {}).get('@id'))},
            'value': list_sum(excreta_n_product.get('value', [])) * vsc / 100
        }
        for (excreta_n_product, vsc) in excreta_n_products
        if vsc > 0
    ]

    mass_balance_items = [carbonContent, yield_per_m2, slaughterAge, aqocsed, npp]

    should_run = all([
        is_animalFeed_complete,
        is_product_complete,
        all(mass_balance_items) or excreta_n_products
    ])

    for excreta_product in excreta_vs_products + excreta_n_products:
        term_id = excreta_product.get('term', {}).get('@id')

        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        is_animalFeed_complete=is_animalFeed_complete,
                        is_product_complete=is_product_complete,
                        aqocsed=aqocsed,
                        inputs_c=inputs_c,
                        carbonContent=carbonContent,
                        yield_of_target_species=yield_per_m2,
                        slaughterAge=slaughterAge,
                        netPrimaryProduction=npp,
                        default_using_kg_N=default_using_kg_N)
        logShouldRun(cycle, MODEL, term_id, should_run)

    return should_run, excreta_vs_products, excreta_n_products, mass_balance_items, inputs_c


def run(cycle: dict):
    should_run, excreta_vs_products, excreta_n_products, mass_balance_items, inputs_c = _should_run(cycle)
    return (
        _run(excreta_vs_products, excreta_n_products, mass_balance_items, inputs_c) if should_run else
        # add product without value to show the logs
        _run_no_value(excreta_vs_products, excreta_n_products)
    )
