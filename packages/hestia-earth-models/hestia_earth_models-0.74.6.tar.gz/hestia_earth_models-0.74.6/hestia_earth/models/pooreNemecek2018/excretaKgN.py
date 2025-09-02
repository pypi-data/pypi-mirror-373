from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _omit
from hestia_earth.models.utils.property import _get_nitrogen_content
from hestia_earth.models.utils.input import get_feed_inputs
from hestia_earth.models.utils.product import _new_product, get_animal_produced_nitrogen
from hestia_earth.models.utils.blank_node import convert_to_nitrogen
from .utils import get_excreta_product_with_ratio
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.product": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": ["liveAnimal", "animalProduct", "liveAquaticSpecies"],
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
        }],
        "or": [
            {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "term.units": "kg",
                        "value": "> 0",
                        "properties": [
                            {"@type": "Property", "value": "", "term.@id": "nitrogenContent"},
                            {"@type": "Property", "value": "", "term.@id": "crudeProteinContent"}
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
                        {"@type": "Property", "value": "", "term.@id": "nitrogenContent"},
                        {"@type": "Property", "value": "", "term.@id": "crudeProteinContent"}
                    ]
                }]
            }
        ],
        "optional": {
            "practices": [{"@type": "Practice", "term.termType": "system"}]
        }
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
LOOKUPS = {
    "crop-property": ["nitrogenContent", "crudeProteinContent"],
    "animalProduct": ["excretaKgNTermIds"],
    "liveAnimal": ["excretaKgNTermIds"],
    "liveAquaticSpecies": ["excretaKgNTermIds"]
}
MODEL_KEY = 'excretaKgN'


def _product(excreta_product: str, value: float = None):
    product = _new_product(excreta_product.get('term', {}).get('@id'), value, MODEL)
    return _omit(excreta_product, ['value']) | product


def _run_no_value(excreta_products: list):
    return [_product(excreta_product) for excreta_product in excreta_products]


def _run(excreta_products: list, mass_balance_items: list, alternate_items: list):
    inputs_n, products_n = mass_balance_items
    product_value, nitrogen_content = alternate_items
    value = inputs_n - products_n if all(mass_balance_items) else 3.31 * product_value * nitrogen_content / 100
    # ratio is stored in product value
    return [
        _product(excreta_product, round(value * excreta_product.get('value')[0] / 100, 7))
        for excreta_product in excreta_products
    ] if value > 0 else []


def _should_run(cycle: dict):
    primary_prod = find_primary_product(cycle) or {}

    excreta_products = get_excreta_product_with_ratio(cycle, 'excretaKgNTermIds', model_key=MODEL_KEY)
    first_term_id = excreta_products[0].get('term', {}).get('@id') if excreta_products else None

    dc = cycle.get('completeness', {})
    is_animalFeed_complete = dc.get('animalFeed', False)
    is_product_complete = dc.get('product', False)

    inputs_feed = get_feed_inputs(cycle)
    inputs_n = convert_to_nitrogen(cycle, MODEL, inputs_feed, term=first_term_id, model_key=MODEL_KEY)

    products_n = get_animal_produced_nitrogen(MODEL, cycle.get('products', []))

    # we can still run the model for `liveAquaticSpecies`
    is_liveAquaticSpecies = primary_prod.get('term', {}).get('termType') == TermTermType.LIVEAQUATICSPECIES.value
    product_value = list_sum(primary_prod.get('value', [0]))
    nitrogen_content = _get_nitrogen_content(primary_prod)

    mass_balance_items = [inputs_n, products_n]
    alternate_items = [product_value, nitrogen_content]

    should_run = all([
        is_animalFeed_complete,
        is_product_complete,
        any([
            all(mass_balance_items),
            is_liveAquaticSpecies and all(alternate_items)
        ])
    ])

    for excreta_product in excreta_products:
        term_id = excreta_product.get('term', {}).get('@id')

        if is_liveAquaticSpecies:
            logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                            is_liveAquaticSpecies=is_liveAquaticSpecies,
                            product_value=product_value,
                            nitrogen_content=nitrogen_content,
                            inputs_n=inputs_n,
                            products_n=products_n)

        else:
            logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                            is_animalFeed_complete=is_animalFeed_complete,
                            is_product_complete=is_product_complete,
                            inputs_n=inputs_n,
                            products_n=products_n)

        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    return should_run, excreta_products, mass_balance_items, alternate_items


def run(cycle: dict):
    should_run, excreta_products, mass_balance_items, alternate_items = _should_run(cycle)
    return (
        _run(excreta_products, mass_balance_items, alternate_items) if should_run else
        # add product without value to show the logs
        _run_no_value(excreta_products)
    )
