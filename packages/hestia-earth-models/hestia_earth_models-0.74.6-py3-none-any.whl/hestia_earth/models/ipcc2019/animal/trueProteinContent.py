from .utils import should_run_by_productivity_lookup, run_animal_by_productivity

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        },
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "practices": [{
                "@type": "Practice",
                "term.termType": "animalManagement"
            }]
        }]
    }
}
LOOKUPS = {
    "region-liveAnimal-milkTrueProteinContent": "",
    "liveAnimal": "milkYieldPracticeTermIds"
}
RETURNS = {
    "Animal": [{
        "practices": [{
            "@type": "Practice",
            "value": ""
        }]
    }]
}
TERM_ID = 'trueProteinContent'


def run(cycle: dict):
    animals = should_run_by_productivity_lookup(
        TERM_ID, cycle, list(LOOKUPS.keys())[0], practice_column=LOOKUPS['liveAnimal']
    )
    return list(map(run_animal_by_productivity(TERM_ID, include_practice=True), animals))
