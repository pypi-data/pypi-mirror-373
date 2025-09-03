from hestia_earth.schema import EmissionMethodTier, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission, get_nh3_no3_nox_to_n
from .utils import COEFF_NH3NOX_N2O, COEFF_NO3_N2O
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "no3ToGroundwaterExcreta"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirExcreta"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirExcreta"}
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2OToAirExcretaIndirect'
TIER = EmissionMethodTier.TIER_1.value
NO3_TERM_ID = 'no3ToGroundwaterExcreta'
NH3_TERM_ID = 'nh3ToAirExcreta'
NOX_TERM_ID = 'noxToAirExcreta'


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(no3_n: float, nh3_n: float, nox_n: float):
    value = COEFF_NH3NOX_N2O * (nh3_n + nox_n) + COEFF_NO3_N2O * no3_n
    return [_emission(value * get_atomic_conversion(Units.KG_N2O, Units.TO_N))]


def _should_run(cycle: dict):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    term_type_complete = _is_term_type_complete(cycle, TermTermType.EXCRETA)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    no3ToGroundwaterExcreta_to_n=no3_n,
                    nh3ToAirExcreta_to_n=nh3_n,
                    noxToAirExcreta_to_n=nox_n,
                    term_type_excreta_complete=term_type_complete)

    should_run = all([no3_n is not None, nh3_n is not None, nox_n is not None, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, no3_n, nh3_n, nox_n


def run(cycle: dict):
    should_run, *emissions = _should_run(cycle)
    return _run(*emissions) if should_run else []
