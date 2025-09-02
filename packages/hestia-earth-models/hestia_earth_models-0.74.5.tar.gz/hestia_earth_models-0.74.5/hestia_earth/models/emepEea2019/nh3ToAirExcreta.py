from hestia_earth.schema import EmissionMethodTier, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.input import total_excreta_tan
from hestia_earth.models.utils.excretaManagement import get_excreta_inputs_with_factor
from . import MODEL
from .utils import _emission

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "inputs": [{
            "@type": "Input",
            "value": "",
            "term.termType": "excreta",
            "term.units": "kg N",
            "properties": [
                {"@type": "Property", "value": "", "term.@id": "totalAmmoniacalNitrogenContentAsN"}
            ]
        }],
        "practices": [
            {"@type": "Practice", "value": "", "term.termType": "excretaManagement"}
        ]
    }
}
LOOKUPS = {
    "excretaManagement-excreta-NH3_EF_2019": ""
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
TERM_ID = 'nh3ToAirExcreta'
TIER = EmissionMethodTier.TIER_2.value


def _run(excreta_EF_input: float):
    value = excreta_EF_input * get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    return [_emission(value=value, tier=TIER, term_id=TERM_ID)]


def _should_run(cycle: dict):
    excreta_complete = _is_term_type_complete(cycle, TermTermType.EXCRETA)
    excreta_EF_input = get_excreta_inputs_with_factor(
        cycle, f"{list(LOOKUPS.keys())[0]}.csv", excreta_conversion_func=total_excreta_tan, model=MODEL, term=TERM_ID
    )

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_excreta_complete=excreta_complete,
                    excreta_EF_input=excreta_EF_input)

    should_run = all([excreta_complete, excreta_EF_input >= 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excreta_EF_input


def run(cycle: dict):
    should_run, excreta_EF_input = _should_run(cycle)
    return _run(excreta_EF_input) if should_run else []
