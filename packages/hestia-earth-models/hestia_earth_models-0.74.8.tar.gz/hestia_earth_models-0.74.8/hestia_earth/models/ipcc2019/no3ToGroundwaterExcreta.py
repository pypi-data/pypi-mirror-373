from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType, SiteSiteType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_excreta_N_total, get_ecoClimateZone
from hestia_earth.models.utils.input import total_excreta
from hestia_earth.models.utils.excretaManagement import get_excreta_inputs_with_factor
from .utils import get_FracLEACH_H
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "excreta",
                "properties": [
                    {"@type": "Property", "value": "", "term.@id": "nitrogenContent"},
                    {"@type": "Property", "value": "", "term.@id": "totalAmmoniacalNitrogenContentAsN"}
                ]
            }
        ],
        "site": {
            "@type": "Site",
            "optional": {
                "measurements": [{"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}]
            }
        },
        "optional": {
            "completeness.water": "True",
            "practices": [
                {"@type": "Practice", "value": "", "term.termType": "waterRegime"},
                {"@type": "Practice", "value": "", "term.termType": "excretaManagement"}
            ]
        }
    }
}
LOOKUPS = {
    "excretaManagement-excreta-NO3_EF_2019": ""
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'no3ToGroundwaterExcreta'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, sd: float = None, min: float = None, max: float = None):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    if sd is not None:
        emission['sd'] = [sd]
        emission['min'] = [min]
        emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict):
    N_total = get_excreta_N_total(cycle)
    value, min, max, sd = get_FracLEACH_H(cycle, TERM_ID)
    converted_N_total = N_total * get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    return [_emission(
        converted_N_total * value,
        converted_N_total * sd,
        converted_N_total * min,
        converted_N_total * max
    )]


def _run_with_excreta_managemen(excreta_EF_input: float):
    value = excreta_EF_input * get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    return [_emission(value)]


def _should_run_with_excreta_management(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    return site_type not in [SiteSiteType.CROPLAND.value, SiteSiteType.PERMANENT_PASTURE.value]


def _should_run(cycle: dict):
    N_excreta = get_excreta_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)
    excreta_complete = _is_term_type_complete(cycle, TermTermType.EXCRETA)
    water_complete = _is_term_type_complete(cycle, TermTermType.WATER)

    use_excreta_management = _should_run_with_excreta_management(cycle)
    excreta_EF_input = get_excreta_inputs_with_factor(
        cycle, f"{list(LOOKUPS.keys())[0]}.csv", excreta_conversion_func=total_excreta, model=MODEL, term=TERM_ID
    ) if use_excreta_management else None

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_excreta=N_excreta,
                    ecoClimateZone=ecoClimateZone,
                    term_type_excreta_complete=excreta_complete,
                    term_type_water_complete=water_complete,
                    excreta_EF_input=excreta_EF_input)

    should_run = excreta_complete and (
        all([excreta_EF_input >= 0]) if use_excreta_management else
        all([water_complete, N_excreta is not None, ecoClimateZone])
    )
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, excreta_EF_input


def run(cycle: dict):
    should_run, excreta_EF_input = _should_run(cycle)
    return (
        _run_with_excreta_managemen(excreta_EF_input) if _should_run_with_excreta_management(cycle) else
        _run(cycle)
    ) if should_run else []
