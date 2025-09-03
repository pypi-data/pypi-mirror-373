from hestia_earth.schema import EmissionMethodTier, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta
from hestia_earth.models.utils.excretaManagement import get_lookup_factor
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "completeness.excreta": "True",
            "inputs": [
                {"@type": "Input", "term.termType": "excreta", "units": "kg N"}
            ]
        },
        "practices": [
            {"@type": "Practice", "value": "", "term.termType": "excretaManagement"}
        ]
    }
}
LOOKUPS = {
    "excretaManagement": "EF_N2O-N"
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
TERM_ID = 'n2OToAirExcretaDirect'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(N_total: float, N2O_N_EF: float):
    value = (N2O_N_EF or 0) * (N_total or 0) * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    N_total = total_excreta(cycle.get('inputs', []))
    N2O_N_EF = get_lookup_factor(cycle.get('practices', []), LOOKUPS['excretaManagement'])
    term_type_complete = _is_term_type_complete(cycle, TermTermType.EXCRETA)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_total=N_total,
                    N2O_N_EF=N2O_N_EF,
                    term_type_excreta_complete=term_type_complete)

    should_run = all([N_total is not None, N2O_N_EF is not None]) or all([not N_total, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_total, N2O_N_EF


def run(cycle: dict):
    should_run, N_total, N2O_N_EF = _should_run(cycle)
    return _run(N_total, N2O_N_EF) if should_run else []
