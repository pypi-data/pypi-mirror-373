from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.blank_node import lookups_logs, properties_logs
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.term import get_wool_terms
from hestia_earth.models.utils.completeness import _is_term_type_complete, _is_term_type_incomplete
from hestia_earth.models.utils.cycle import get_animals_by_period
from . import MODEL
from .pastureGrass_utils import (
    practice_input_id,
    should_run_practice,
    calculate_meanDE,
    calculate_meanECHHV,
    calculate_REM,
    calculate_REG,
    calculate_NEfeed,
    calculate_GE,
    product_wool_energy,
    get_animal_values
)

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.animalPopulation": "True",
        "completeness.freshForage": "False",
        "site": {
            "@type": "Site",
            "siteType": "permanent pasture"
        },
        "practices": [
            {
                "@type": "Practice",
                "value": "",
                "term.termType": "system"
            },
            {
                "@type": "Practice",
                "value": "",
                "term.@id": "pastureGrass",
                "key": {
                    "@type": "Term",
                    "term.termType": "landCover"
                }
            }
        ],
        "inputs": [{
            "@type": "Input",
            "term.units": "kg",
            "value": "> 0",
            "isAnimalFeed": "True",
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                }]
            }
        }],
        "animals": [{
            "@type": "Animal",
            "value": "> 0",
            "term.termType": "liveAnimal",
            "referencePeriod": "average",
            "properties": [{
                "@type": "Property",
                "value": "",
                "term.@id": [
                    "liveweightPerHead",
                    "weightAtMaturity"
                ]
            }],
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": [
                        "hoursWorkedPerDay",
                        "pregnancyRateTotal",
                        "animalsPerBirth"
                    ]
                }],
                "inputs": [{
                    "@type": "Input",
                    "term.units": "kg",
                    "value": "> 0",
                    "optional": {
                        "properties": [{
                            "@type": "Property",
                            "value": "",
                            "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                        }]
                    }
                }],
                "practices": [{
                    "@type": "Practice",
                    "value": "",
                    "term.termType": "animalManagement",
                    "properties": [{
                        "@type": "Property",
                        "value": "",
                        "term.@id": "fatContent"
                    }]
                }]
            }
        }],
        "optional": {
            "products": [{
                "@type": "Product",
                "value": "",
                "term.@id": "animalProduct"
            }]
        }
    }
}
LOOKUPS = {
    "animalManagement": [
        "mjKgEvMilkIpcc2019",
        "defaultFatContentEvMilkIpcc2019"
    ],
    "animalProduct": ["mjKgEvWoolNetEnergyWoolIpcc2019"],
    "liveAnimal": [
        "ipcc2019AnimalTypeGrouping",
        "mjDayKgCfiNetEnergyMaintenanceIpcc2019",
        "ratioCPregnancyNetEnergyPregnancyIpcc2019",
        "ratioCNetEnergyGrowthCattleBuffaloIpcc2019",
        "mjKgABNetEnergyGrowthSheepGoatsIpcc2019",
        "isWoolProducingAnimal"
    ],
    "system-liveAnimal-activityCoefficient-ipcc2019": "",
    "landCover": "grazedPastureGrassInputId",
    "crop-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "crop": "grazedPastureGrassInputId",
    "forage-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "feedFoodAdditive": "hasEnergyContent",
    "feedFoodAdditive-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"]
}
RETURNS = {
    "Input": [{
        "term.termType": ["crop", "forage"],
        "value": "",
        "isAnimalFeed": "True"
    }]
}
MODEL_KEY = 'pastureGrass'


def _input(term_id: str, value: float):
    node = _new_input(term_id, MODEL)
    node['value'] = [value]
    node['isAnimalFeed'] = True
    return node


def calculate_NEwool(cycle: dict) -> float:
    term_ids = get_wool_terms()
    products = [p for p in cycle.get('products', []) if p.get('term', {}).get('@id') in term_ids]
    product_values = [
        (list_sum(p.get('value', [])), product_wool_energy(p)) for p in products
    ]
    return sum([value * lookup_value for (value, lookup_value) in product_values])


def _run_practice(cycle: dict, meanDE: float, meanECHHV: float, REM: float, REG: float, systems: list):
    animals = get_animals_by_period(cycle)
    NEwool = calculate_NEwool(cycle)
    NEm_feed, NEg_feed, log_feed = calculate_NEfeed(cycle)

    animal_values = [{
        'id': animal.get('term', {}).get('@id')
    } | get_animal_values(cycle, animal, systems) for animal in animals]

    GE = (
        calculate_GE(animal_values, REM, REG, NEwool, NEm_feed, NEg_feed) / (meanDE/100)
    ) if meanDE else 0

    def run(practice: dict):
        key = practice.get('key', {})
        key_id = key.get('@id')
        input_term_id = practice_input_id(practice)
        value = (GE / meanECHHV) * (list_sum(practice.get('value', [0])) / 100)

        logs = log_as_table([v | {
            'NEwool': NEwool,
            'total-feed-NEm': NEm_feed,
            'total-feed-NEg': NEg_feed,
            'practiceKeyId': key_id,
            'GE': GE
        } for v in animal_values])
        animal_lookups = lookups_logs(MODEL, animals, LOOKUPS, model_key=MODEL_KEY, term=input_term_id)
        animal_properties = properties_logs(animals, properties=[
            'liveweightPerHead',
            'hoursWorkedPerDay',
            'animalsPerBirth',
            'pregnancyRateTotal',
            'weightAtMaturity',
            'liveweightGain',
            'weightAtWeaning',
            'weightAtOneYear',
            'weightAtSlaughter'
        ])
        has_positive_feed_values = all([NEm_feed >= 0, NEg_feed >= 0])

        logRequirements(cycle, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        feed_logs=log_as_table(log_feed),
                        has_positive_feed_values=has_positive_feed_values,
                        animal_logs=logs,
                        animal_lookups=animal_lookups,
                        animal_properties=animal_properties)

        should_run = all([has_positive_feed_values])
        logShouldRun(cycle, MODEL, input_term_id, should_run, model_key=MODEL_KEY)

        return _input(input_term_id, value) if should_run else None

    return run


def _should_run(cycle: dict, practices: dict):
    systems = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM)
    animalFeed_complete = _is_term_type_complete(cycle, 'animalFeed')
    animalPopulation_complete = _is_term_type_complete(cycle, 'animalPopulation')
    freshForage_incomplete = _is_term_type_incomplete(cycle, 'freshForage')
    all_animals_have_value = all([a.get('value', 0) > 0 for a in cycle.get('animals', [])])

    has_cycle_inputs_feed = any([i.get('isAnimalFeed', False) for i in cycle.get('inputs', [])])

    meanDE = calculate_meanDE(practices)
    meanECHHV = calculate_meanECHHV(practices)
    REM = calculate_REM(meanDE)
    REG = calculate_REG(meanDE)

    has_practice_termType_system = len(systems) > 0
    has_practice_pastureGrass_with_landCover_key = len(practices) > 0

    should_run = all([
        animalFeed_complete,
        animalPopulation_complete,
        freshForage_incomplete,
        has_cycle_inputs_feed,
        all_animals_have_value,
        has_practice_termType_system,
        has_practice_pastureGrass_with_landCover_key,
        meanDE > 0,
        meanECHHV > 0
    ])

    for term_id in [practice_input_id(p) for p in practices] or [MODEL_KEY]:
        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        term_type_animalFeed_complete=animalFeed_complete,
                        term_type_animalPopulation_complete=animalPopulation_complete,
                        term_type_freshForage_incomplete=freshForage_incomplete,
                        has_cycle_inputs_feed=has_cycle_inputs_feed,
                        all_animals_have_value=all_animals_have_value,
                        has_practice_termType_system=has_practice_termType_system,
                        has_practice_pastureGrass_with_landCover_key=has_practice_pastureGrass_with_landCover_key,
                        grass_MeanDE=calculate_meanDE(practices, term=term_id),
                        grass_MeanECHHV=calculate_meanECHHV(practices, term=term_id),
                        grass_REM=REM,
                        grass_REG=REG)

        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    return should_run, meanDE, meanECHHV, REM, REG, systems


def run(cycle: dict):
    practices = list(filter(should_run_practice(cycle), cycle.get('practices', [])))
    should_run, meanDE, meanECHHV, REM, REG, systems = _should_run(cycle, practices)
    return non_empty_list(
        map(_run_practice(cycle, meanDE, meanECHHV, REM, REG, systems), practices)
    ) if should_run else []
