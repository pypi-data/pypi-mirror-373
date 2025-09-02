from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_crop_residue_decomposition_N_total
from hestia_earth.models.utils.product import has_flooded_rice
from .utils import N2O_FACTORS
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "cropResidue",
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
        "optional": {
            "products": [{"@type": "Product", "term.@id": "riceGrainInHuskFlooded"}]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "cropResidue": "decomposesOnField"
}
TERM_ID = 'n2OToAirCropResidueDecompositionDirect'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, min: float, max: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    flooded_rice = has_flooded_rice(cycle.get('products', []))

    converted_N_total = N_total * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    factors = N2O_FACTORS['flooded_rice'] if flooded_rice else N2O_FACTORS['default']

    debugValues(cycle, model=MODEL, term=TERM_ID,
                has_flooded_rice=flooded_rice,
                factors_used=log_as_table(factors))

    value = converted_N_total * factors['value']
    min = converted_N_total * factors['min']
    max = converted_N_total * factors['max']
    return [_emission(value, min, max)]


def _should_run(cycle: dict):
    term_type_complete = _is_term_type_complete(cycle, TermTermType.CROPRESIDUE)
    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_complete=term_type_complete,
                    N_crop_residue=N_crop_residue)

    should_run = all([N_crop_residue is not None, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_crop_residue


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
