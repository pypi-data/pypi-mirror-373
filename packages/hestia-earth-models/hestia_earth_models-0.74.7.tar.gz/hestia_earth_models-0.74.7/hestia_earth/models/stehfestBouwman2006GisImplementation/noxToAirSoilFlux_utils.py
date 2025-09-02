from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.cycle import (
    get_crop_residue_decomposition_N_total, get_excreta_N_total,
    get_organic_fertiliser_N_total, get_inorganic_fertiliser_N_total
)
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "completeness.cropResidue": "True",
        "completeness.fertiliser": "True",
        "inputs": [{
            "@type": "Input",
            "value": "",
            "term.units": ["kg", "kg N"],
            "term.termType": ["organicFertiliser", "inorganicFertiliser", "excreta"],
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
        }],
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": ["cropResidue", "excreta"],
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
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
TERM_ID = 'noxToAirSoilFlux'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _should_run(cycle: dict, term=TERM_ID, tier=TIER):
    country = cycle.get('site', {}).get('country', {})

    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    N_excreta = get_excreta_N_total(cycle)
    N_total = list_sum([
        N_crop_residue,
        N_organic_fertiliser,
        N_inorganic_fertiliser,
        N_excreta
    ])

    logRequirements(cycle, model=MODEL, term=term,
                    country=country.get('@id'),
                    N_total=N_total,
                    N_crop_residue=N_crop_residue,
                    N_organic_fertiliser=N_organic_fertiliser,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    N_excreta=N_excreta)

    should_run = all([country, N_total >= 0])
    logShouldRun(cycle, MODEL, term, should_run, methodTier=tier)
    return should_run, country, N_total


def _get_value(cycle: dict, country: dict, N_total: float, term=TERM_ID):
    EF_NOX = safe_parse_float(get_lookup_value(country, LOOKUPS['region'], model=MODEL, term=TERM_ID), default=0)
    debugValues(cycle, model=MODEL, term=term,
                EF_NOX=EF_NOX)
    return EF_NOX * N_total


def _run(cycle: dict, country: dict, N_total: float):
    value = _get_value(cycle, country, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, country, N_total = _should_run(cycle)
    return _run(cycle, country, N_total) if should_run else []
