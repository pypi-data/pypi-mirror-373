from hestia_earth.schema import EmissionMethodTier

from .utils import _emission, get_live_animal_emission_value, should_run_animal
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalPopulation": "True",
        "site": {"@type": "Site"},
        "siteDuration": "",
        "animals": [
            {
                "@type": "Animal",
                "term.termType": "liveAnimal",
                "value": "",
                "referencePeriod": "average"
            }
        ],
        "optional": {
            "otherSites": [{"@type": "Site"}],
            "otherSitesDuration": ""
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "liveAnimal": "pm25ToAirEea2019",
    "operation": "pm25ToAirAnimalHousingEmepEea2019"
}
TERM_ID = 'pm25ToAirAnimalHousing'
TIER = EmissionMethodTier.TIER_1.value


def _run(animals: list[dict], total_duration: float):
    return [
        _emission(
            value=get_live_animal_emission_value(animals, total_duration, lookup_col=LOOKUPS["liveAnimal"]),
            tier=TIER,
            term_id=TERM_ID
        )
    ]


def run(cycle: dict):
    should_run, animals, total_duration = should_run_animal(
        cycle=cycle, model=MODEL, term=TERM_ID, tier=TIER
    )
    return _run(animals, total_duration) if should_run else []
