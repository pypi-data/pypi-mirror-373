from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.constant import Units, convert_to_unit, get_atomic_conversion
from hestia_earth.models.utils.product import convert_product_to_unit
from hestia_earth.models.utils.completeness import _is_term_type_complete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.product": "True",
        "completeness.fertiliser": "True",
        "completeness.liveAnimalInput": "True",
        "inputs": [
            {
                "@type": "Input",
                "term.termType": [
                    "crop",
                    "liveAnimal",
                    "liveAquaticSpecies",
                    "animalProduct",
                    "processedFood",
                    "feedFoodAdditive",
                    "organicFertiliser",
                    "forage",
                    "excreta",
                    "waste"
                ],
                "optional": {
                    "properties": [
                        {"@type": "Property", "value": "", "term.@id": "phosphorusContentAsP"},
                        {"@type": "Property", "value": "", "term.@id": "phosphateContentAsP2O5"}
                    ]
                }
            },
            {
                "@type": "Input",
                "term.termType": "inorganicFertiliser",
                "term.units": "kg P2O5"
            }
        ],
        "products": [{
            "@type": "Product",
            "term.termType": ["liveAquaticSpecies", "liveAnimal", "animalProduct", "crop"],
            "optional": {
                "properties": [
                    {"@type": "Property", "value": "", "term.@id": "phosphorusContentAsP"},
                    {"@type": "Property", "value": "", "term.@id": "phosphateContentAsP2O5"}
                ]
            }
        }]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'pToSurfaceWaterAquacultureSystems'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodTier'] = TIER
    return emission


def _convert_to_P(blank_node: dict):
    return {
        'id': blank_node.get('term', {}).get('@id'),
        'value': list_sum(blank_node.get('value'), default=None),
        'value-converted': (
            convert_product_to_unit(blank_node, Units.KG_P) or
            convert_product_to_unit(blank_node, Units.KG_P2O5) / get_atomic_conversion(Units.KG_P2O5, Units.KG_P) or
            convert_to_unit(blank_node, Units.KG_P)
        )
    }


def _run(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), [
        TermTermType.CROP,
        TermTermType.LIVEANIMAL,
        TermTermType.LIVEAQUATICSPECIES,
        TermTermType.ANIMALPRODUCT,
        TermTermType.PROCESSEDFOOD,
        TermTermType.FEEDFOODADDITIVE,
        TermTermType.ORGANICFERTILISER,
        TermTermType.FORAGE,
        TermTermType.EXCRETA,
        TermTermType.WASTE,
    ]) + _filter_list_term_unit(filter_list_term_type(cycle.get('inputs', []), [
        TermTermType.INORGANICFERTILISER
    ]), Units.KG_P2O5)
    inputs_P = list(map(_convert_to_P, inputs))
    total_inputs_P = list_sum(non_empty_list([i.get('value-converted', 0) for i in inputs_P]))

    products = filter_list_term_type(cycle.get('products', []), [
        TermTermType.CROP,
        TermTermType.LIVEANIMAL,
        TermTermType.LIVEAQUATICSPECIES,
        TermTermType.ANIMALPRODUCT
    ])
    products_P = list(map(_convert_to_P, products))
    total_products_P = list_sum(non_empty_list([i.get('value-converted', 0) for i in products_P]))

    debugValues(cycle, model=MODEL, term=TERM_ID,
                inputs_P=log_as_table(inputs_P),
                products_P=log_as_table(products_P))

    return [_emission(total_inputs_P - total_products_P)]


def _should_run(cycle: dict):
    is_animalFeed_complete = _is_term_type_complete(cycle, 'animalFeed')
    is_product_complete = _is_term_type_complete(cycle, 'product')
    is_fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')
    is_liveAnimalInput_complete = _is_term_type_complete(cycle, 'liveAnimalInput')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    is_term_type_animalFeed_complete=is_animalFeed_complete,
                    is_term_type_product_complete=is_product_complete,
                    is_term_type_fertiliser_complete=is_fertiliser_complete,
                    is_term_type_liveAnimalInput_complete=is_liveAnimalInput_complete)

    should_run = all([
        is_animalFeed_complete,
        is_product_complete,
        is_fertiliser_complete,
        is_liveAnimalInput_complete
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
