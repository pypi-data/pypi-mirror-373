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
            "none": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": "liveweightPerHead"
                }]
            }
        }]
    }
}
LOOKUPS = {
    "region-liveAnimal-liveweightPerHead": ""
}
RETURNS = {
    "Animal": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'liveweightPerHead'


def run(cycle: dict):
    animals = should_run_by_productivity_lookup(TERM_ID, cycle, list(LOOKUPS.keys())[0])
    return list(map(run_animal_by_productivity(TERM_ID), animals))
