from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.cycle import get_animals_by_period
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL


def _emission(value: float, tier: str, term_id: str, input: dict = None, operation: dict = None):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = tier
    if input:
        emission['inputs'] = [input]
    if operation:
        emission['operation'] = operation
    return emission


def _get_emissions_factor(animal: dict, lookup_col: str) -> float:
    return safe_parse_float(
        get_lookup_value(animal.get("term", {}), lookup_col, model=MODEL, term=animal.get("term", "")),
        default=None
    )


def _duration_in_housing(cycle: dict) -> int:
    other_sites = cycle.get("otherSites", [])
    other_durations = cycle.get("otherSitesDuration", [])
    return list_sum([
        cycle.get("siteDuration", cycle.get("cycleDuration", 0))
        if cycle.get("site", {}).get("siteType", "") == SiteSiteType.ANIMAL_HOUSING.value else 0
    ] + ([
        other_durations[x]
        for x in range(len(other_sites))
        if other_sites[x].get("siteType", "") == SiteSiteType.ANIMAL_HOUSING.value
    ] if len(other_sites) == len(other_durations) else []))


def get_live_animal_emission_value(animals: list[dict], duration: float, lookup_col: str) -> float:
    return list_sum([
        animal.get('value') * _get_emissions_factor(animal=animal, lookup_col=lookup_col)
        for animal in animals
    ]) * duration / 365


def should_run_animal(cycle: dict, model: str, term: str, tier: str) -> tuple[list, bool]:
    term_type_animalPopulation_complete = _is_term_type_complete(cycle=cycle, term="animalPopulation")

    # models will be set as not relevant is primary `siteType` does not match, so check only `otherSites`.

    total_duration = _duration_in_housing(cycle)

    has_other_sites_and_duration = len(cycle.get("otherSites", [])) == len(cycle.get("otherSitesDuration", []))

    animals = get_animals_by_period(cycle)
    has_animals = len(animals) > 0

    logRequirements(cycle, model=model, term=term,
                    term_type_animalPopulation_complete=term_type_animalPopulation_complete,
                    has_animals=has_animals,
                    has_other_sites_and_duration=has_other_sites_and_duration,
                    number_of_days_in_animal_housing=total_duration)

    should_run = all([term_type_animalPopulation_complete, has_animals, has_other_sites_and_duration])
    logShouldRun(cycle, model, term, should_run, methodTier=tier)
    return should_run, animals, total_duration
