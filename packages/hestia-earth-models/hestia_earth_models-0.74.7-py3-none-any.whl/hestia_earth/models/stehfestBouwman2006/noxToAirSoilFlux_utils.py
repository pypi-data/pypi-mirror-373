import math
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.cycle import (
    get_crop_residue_decomposition_N_total, get_excreta_N_total,
    get_organic_fertiliser_N_total, get_inorganic_fertiliser_N_total
)
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
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
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "totalNitrogenPerKgSoil"},
                {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
LOOKUPS = {
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_NOX-N_FACTOR"
}
TERM_ID = 'noxToAirSoilFlux'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _should_run(cycle: dict, term=TERM_ID, tier=TIER):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    totalNitrogenPerKgSoil = most_relevant_measurement_value(measurements, 'totalNitrogenPerKgSoil', end_date)

    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    N_excreta = get_excreta_N_total(cycle)
    N_total = list_sum(non_empty_list([
        N_crop_residue,
        N_organic_fertiliser,
        N_inorganic_fertiliser,
        N_excreta
    ]))

    logRequirements(cycle, model=MODEL, term=term,
                    ecoClimateZone=ecoClimateZone,
                    totalNitrogenPerKgSoil=totalNitrogenPerKgSoil,
                    N_total=N_total,
                    N_crop_residue=N_crop_residue,
                    N_organic_fertiliser=N_organic_fertiliser,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    N_excreta=N_excreta)

    should_run = all([
        ecoClimateZone,
        totalNitrogenPerKgSoil,
        N_total >= 0
    ])
    logShouldRun(cycle, MODEL, term, should_run, methodTier=tier)
    return should_run, ecoClimateZone, totalNitrogenPerKgSoil, N_total


def _get_value(cycle: dict, ecoClimateZone: str, nitrogenContent: float, N_total: float, term=TERM_ID):
    eco_factor = get_ecoClimateZone_lookup_value(ecoClimateZone, 'STEHFEST_BOUWMAN_2006_NOX-N_FACTOR')
    nitrogen_factor = 0 if nitrogenContent < 0.5 else -1.0211 if nitrogenContent <= 2 else 0.7892
    conversion_unit = get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    try:
        value = min(
            0.025 * N_total,
            math.exp(-0.451 + 0.0061 * N_total + nitrogen_factor + eco_factor) -
            math.exp(-0.451 + nitrogen_factor + eco_factor)
        )
    except OverflowError:
        value = 0.025 * N_total

    debugValues(cycle, model=MODEL, term=term,
                eco_factor=eco_factor,
                nitrogen_factor=nitrogen_factor,
                conversion_unit=conversion_unit)

    return value * conversion_unit


def _run(cycle: dict, eecoClimateZone: str, nitrogenContent: float, N_total: float):
    value = _get_value(cycle, eecoClimateZone, nitrogenContent, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, ecoClimateZone, nitrogenContent, N_total = _should_run(cycle)
    return _run(cycle, ecoClimateZone, nitrogenContent, N_total) if should_run else []
