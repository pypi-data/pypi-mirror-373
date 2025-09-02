from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.aggregated import should_link_input_to_impact, link_inputs_to_impact

REQUIREMENTS = {
    "Cycle": {
        "animals": [{
            "@type": "Animal",
            "inputs": [{
                "@type": "Input",
                "value": "",
                "none": {
                    "impactAssessment": {"@type": "ImpactAssessment"},
                    "fromCycle": "True",
                    "producedInCycle": "True"
                },
                "optional": {
                    "country": {"@type": "Term", "termType": "region"},
                    "region": {"@type": "Term", "termType": "region"}
                }
            }]
        }]
    }
}
RETURNS = {
    "Animal": [{
        "inputs": [{
            "@type": "Input",
            "impactAssessment": "",
            "impactAssessmentIsProxy": "True"
        }]
    }]
}
MODEL_ID = 'hestiaAggregatedData'
MODEL_KEY = 'impactAssessment'


def _run_animal_input(cycle: dict, animal: dict, input: dict):
    inputs = link_inputs_to_impact(MODEL_ID, cycle, [input], animalId=animal.get('animalId'))
    return inputs[0] if inputs else input


def _run_animal(cycle: dict, animal: dict):
    return animal | {
        'inputs': [
            (
                _run_animal_input(cycle, animal, input) if should_link_input_to_impact(cycle)(input) else input
            ) for input in animal.get('inputs', [])
        ]
    }


def _should_run_animal(cycle: dict, animal: dict):
    end_date = cycle.get('endDate')
    term_id = animal.get('term', {}).get('@id')
    inputs = animal.get('inputs', [])
    inputs = list(filter(should_link_input_to_impact(cycle), inputs))
    nb_inputs = len(inputs)

    logRequirements(cycle, model=MODEL_ID, term=term_id, key=MODEL_KEY, animalId=animal.get('animalId'),
                    end_date=end_date,
                    nb_inputs=nb_inputs)

    should_run = all([end_date, nb_inputs > 0])
    logShouldRun(cycle, MODEL_ID, term_id, should_run, key=MODEL_KEY, animalId=animal.get('animalId'))
    return should_run, inputs


def run(cycle: dict):
    animals = list(filter(lambda a: _should_run_animal(cycle, a), cycle.get('animals', [])))
    return list(map(lambda a: _run_animal(cycle, a), animals))
