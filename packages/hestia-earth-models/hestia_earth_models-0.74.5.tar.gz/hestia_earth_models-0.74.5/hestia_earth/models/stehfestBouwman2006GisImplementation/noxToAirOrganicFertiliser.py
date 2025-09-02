from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import get_organic_fertiliser_N_total
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from .noxToAirSoilFlux_utils import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.units": ["kg", "kg N"],
                "term.termType": "organicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
            }
        ],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
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
    "region": "EF_NOX"
}
TERM_ID = 'noxToAirOrganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, country_id: str, N_total: float):
    noxToAirSoilFlux = _get_value(cycle, country_id, N_total, TERM_ID)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    value = N_organic_fertiliser / N_total * noxToAirSoilFlux if all([
        N_organic_fertiliser, N_total
    ]) else 0
    return [_emission(value)]


def run(cycle: dict):
    default_should_run, country_id, N_total, *args = _should_run(cycle, TERM_ID, TIER)
    term_type_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_fertiliser_complete=term_type_complete)

    should_run = all([default_should_run, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)

    return _run(cycle, country_id, N_total) if should_run else []
