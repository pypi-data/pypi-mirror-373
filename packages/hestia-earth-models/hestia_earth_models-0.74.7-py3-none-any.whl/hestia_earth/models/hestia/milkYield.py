from hestia_earth.schema import TermTermType, SiteSiteType, PracticeStatsDefinition
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_blank_nodes_id
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.site import valid_site_type
from hestia_earth.models.utils.term import get_lookup_value
from .utils import get_liveAnimal_term_id
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "",
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "permanent pasture", "animal housing"]
        },
        "products": [{
            "@type": "Product",
            "value": "> 0",
            "termType": "animalProduct"
        }],
        "animals": [{
            "@type": "Animal",
            "value": "> 0",
            "termType": "liveAnimal"
        }]
    }
}
RETURNS = {
    "Animal": [{
        "practices": [{
            "@type": "Practice",
            "value": "",
            "min": "",
            "max": "",
            "sd": "",
            "statsDefinition": "modelled"
        }]
    }]
}
LOOKUPS = {
    "animalProduct": ["liveAnimalTermId", "milkYieldPracticeTermId"]
}

MODEL_KEY = 'milkYield'
VALID_SITE_TYPES = [
    SiteSiteType.CROPLAND.value, SiteSiteType.ANIMAL_HOUSING.value, SiteSiteType.PERMANENT_PASTURE.value
]


def practice(term_id: str, value: float, properties: list, sd: float = None, min: float = None, max: float = None):
    data = _new_practice(term_id, MODEL)
    data['value'] = [round(value, 2)]
    if properties:
        data['properties'] = properties
    if sd is not None:
        data['sd'] = [round(sd, 2)]
        data['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    if min is not None:
        data['min'] = [round(min, 2)]
        data['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    if max is not None:
        data['max'] = [round(max, 2)]
        data['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return data


def _practice_id(term: dict):
    value = get_lookup_value(term, LOOKUPS['animalProduct'][1], model=MODEL, model_key=MODEL_KEY)
    return value.split(';')[0] if value else None


def _run(cycle: dict, product: dict):
    cycleDuration = cycle.get('cycleDuration')

    term = product.get('term', {})
    practice_id = _practice_id(term)

    live_animal_term_id = get_liveAnimal_term_id(product, model_key=MODEL_KEY)
    live_animal_node = find_term_match(cycle.get('animals', []), live_animal_term_id)
    animal_value = live_animal_node.get('value', 0)

    value = list_sum(product.get('value')) / cycleDuration / animal_value
    sd = list_sum(product.get('sd')) / cycleDuration / animal_value if all([
        list_sum(product.get('sd', [])) > 0
    ]) else None
    min = list_sum(product.get('min')) / cycleDuration / animal_value if all([
        list_sum(product.get('min', [])) > 0
    ]) else None
    max = list_sum(product.get('max')) / cycleDuration / animal_value if all([
        list_sum(product.get('max', [])) > 0
    ]) else None

    return live_animal_node | {
        'practices': live_animal_node.get('practices', []) + [
            practice(practice_id, value, product.get('properties', []), sd=sd, min=min, max=max)
        ]
    }


def _should_run_product(cycle: dict, product: dict):
    cycleDuration = cycle.get('cycleDuration')
    site_type_valid = valid_site_type(cycle.get('site'), site_types=VALID_SITE_TYPES)

    term = product.get('term', {})
    term_id = term.get('@id')

    has_product_value = list_sum(product.get('value', [])) > 0

    live_animal_term_id = get_liveAnimal_term_id(product, model_key=MODEL_KEY)
    live_animal_node = find_term_match(cycle.get('animals', []), live_animal_term_id)
    has_live_animal_node_value = live_animal_node.get('value', 0) > 0

    practice_id = _practice_id(term)
    has_practice_id = any([
        find_term_match(cycle.get('practices', []), practice_id),
        find_term_match((live_animal_node or {}).get('practices', []), practice_id)
    ])
    missing_milkYield_practice = not has_practice_id

    logRequirements(cycle, model=MODEL, term=term_id,
                    cycleDuration=cycleDuration,
                    site_type_valid=site_type_valid,
                    has_product_value=has_product_value,
                    live_animal_term_id=live_animal_term_id,
                    has_live_animal_node_value=has_live_animal_node_value,
                    practice_id=practice_id,
                    missing_milkYield_practice=missing_milkYield_practice)

    should_run = all([
        cycleDuration, has_product_value, has_live_animal_node_value, practice_id, missing_milkYield_practice
    ])
    logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)
    return should_run


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    products = [p for p in products if _should_run_product(cycle, p)]

    logRequirements(cycle, model=MODEL, term=None,
                    animal_product_ids=log_blank_nodes_id(products))

    should_run = all([products])
    logShouldRun(cycle, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return [_run(cycle, p) for p in products] if should_run else []
