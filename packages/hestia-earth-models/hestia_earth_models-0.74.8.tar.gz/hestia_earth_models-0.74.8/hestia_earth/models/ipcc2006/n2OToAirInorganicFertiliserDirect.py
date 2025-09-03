from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.cycle import get_inorganic_fertiliser_N_total
from hestia_earth.models.utils.crop import get_N2ON_fertiliser_coeff_from_primary_product
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.units": ["kg", "kg N"],
                "term.termType": "inorganicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "inorganicFertiliser"}]
            }
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "crop": "N2ON_FERT"
}
TERM_ID = 'n2OToAirInorganicFertiliserDirect'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, N_total: float):
    coefficient = get_N2ON_fertiliser_coeff_from_primary_product(MODEL, TERM_ID, cycle)
    value = N_total * coefficient * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    N_total = get_inorganic_fertiliser_N_total(cycle)
    term_type_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_total=N_total,
                    term_type_fertiliser_complete=term_type_complete)

    should_run = all([N_total is not None, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_total


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
