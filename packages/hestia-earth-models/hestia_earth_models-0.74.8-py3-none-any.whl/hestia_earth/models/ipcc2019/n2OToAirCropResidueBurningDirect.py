from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.cropResidue import get_crop_residue_burnt_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "products": [{
                "@type": "Product",
                "term.@id": ["aboveGroundCropResidueBurnt", "discardedCropBurnt"],
                "value": ""
            }],
            "completeness.cropResidue": "True"
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
    "emission": ["ipcc2019CropResidueBurningFactor"]
}
TERM_ID = 'n2OToAirCropResidueBurningDirect'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _should_run(cycle: dict):
    crop_residue_burnt_value = get_crop_residue_burnt_value(cycle)
    factor = get_lookup_value({'termType': 'emission', '@id': TERM_ID}, LOOKUPS['emission'][0])

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    crop_residue_burnt_value=crop_residue_burnt_value,
                    burning_factor=factor)

    should_run = all([crop_residue_burnt_value is not None, factor is not None])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, crop_residue_burnt_value, factor


def run(cycle: dict):
    should_run, value, factor = _should_run(cycle)
    return [_emission(value * factor)] if should_run else []
