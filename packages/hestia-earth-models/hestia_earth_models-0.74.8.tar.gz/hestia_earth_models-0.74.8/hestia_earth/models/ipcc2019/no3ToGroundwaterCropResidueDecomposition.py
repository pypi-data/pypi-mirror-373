from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_crop_residue_decomposition_N_total, get_ecoClimateZone
from .utils import get_FracLEACH_H
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "completeness.water": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "cropResidue",
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
        "site": {
            "@type": "Site",
            "measurements": [{"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}]
        },
        "optional": {
            "practices": [{"@type": "Practice", "value": "", "term.termType": "waterRegime"}]
        }
    }
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
LOOKUPS = {
    "cropResidue": "decomposesOnField"
}
TERM_ID = 'no3ToGroundwaterCropResidueDecomposition'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, sd: float, min: float, max: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['sd'] = [sd]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    value, min, max, sd = get_FracLEACH_H(cycle, TERM_ID)
    converted_N_total = N_total * get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    return [_emission(
        converted_N_total * value,
        converted_N_total * sd,
        converted_N_total * min,
        converted_N_total * max
    )]


def _should_run(cycle: dict):
    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)
    crop_residue_complete = _is_term_type_complete(cycle, TermTermType.CROPRESIDUE)
    water_complete = _is_term_type_complete(cycle, TermTermType.WATER)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_crop_residue=N_crop_residue,
                    ecoClimateZone=ecoClimateZone,
                    term_type_cropResidue_complete=crop_residue_complete,
                    term_type_water_complete=water_complete)

    should_run = all([N_crop_residue is not None, ecoClimateZone, crop_residue_complete, water_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, N_crop_residue


def run(cycle: dict):
    should_run, N_crop_residue = _should_run(cycle)
    return _run(cycle, N_crop_residue) if should_run else []
