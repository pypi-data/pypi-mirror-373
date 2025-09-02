from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import multiply_values
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.cropResidue import get_crop_residue_burnt_value
from . import MODEL

TIER = EmissionMethodTier.TIER_1.value
LOOKUP_NAME = 'akagiEtAl2011CropResidueBurningFactor'


def _emission(term_id: str, value: float, sd: float = None):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    if sd is not None:
        emission['sd'] = [sd]
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(term_id: str, value: float, factor: float, factor_sd: float = None):
    return [_emission(term_id, value * factor, multiply_values([value, factor_sd]))]


def _should_run(term_id: str, cycle: dict):
    crop_residue_burnt_value = get_crop_residue_burnt_value(cycle)
    term = {'termType': TermTermType.EMISSION.value, '@id': term_id}
    factor = get_lookup_value(term, LOOKUP_NAME)
    factor_sd = get_lookup_value(term, LOOKUP_NAME + '-sd')

    logRequirements(cycle, model=MODEL, term=term_id,
                    crop_residue_burnt_value=crop_residue_burnt_value,
                    burning_factor=factor,
                    burning_factor_sd=factor_sd)

    should_run = all([crop_residue_burnt_value is not None, factor is not None])
    logShouldRun(cycle, MODEL, term_id, should_run, methodTier=TIER)
    return should_run, crop_residue_burnt_value, factor, factor_sd


def run_emission(term_id: str, cycle: dict):
    should_run, value, factor, factor_sd = _should_run(term_id, cycle)
    return _run(term_id, value, factor, factor_sd) if should_run else []
