from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.product import (
    abg_residue_on_field_nitrogen_content, abg_total_residue_nitrogen_content,
    discarded_residue_on_field_nitrogen_content, discarded_total_residue_nitrogen_content
)
from hestia_earth.models.utils.completeness import _is_term_type_complete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "products": [
                {
                    "@type": "Product",
                    "value": "",
                    "term.@id": [
                        "aboveGroundCropResidueTotal",
                        "aboveGroundCropResidueLeftOnField",
                        "aboveGroundCropResidueIncorporated",
                        "discardedCropTotal",
                        "discardedCropLeftOnField",
                        "discardedCropIncorporated"
                    ],
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            ],
            "completeness.electricityFuel": "True"
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'nh3ToAirCropResidueDecomposition'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, left_on_field_residue: float, total_nitrogenContent: float):
    A = min([
        max([(0.38 * 1000 * total_nitrogenContent/100 - 5.44), 0]) / 100,
        17 / 100
    ])
    debugValues(cycle, model=MODEL, term=TERM_ID,
                A=A)
    value = A * left_on_field_residue * get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    products = cycle.get('products', [])
    term_type_complete = _is_term_type_complete(cycle, TermTermType.CROPRESIDUE)

    left_on_field_residue = list_sum([
        abg_residue_on_field_nitrogen_content(products),
        discarded_residue_on_field_nitrogen_content(products)
    ])
    total_nitrogenContent = list_sum([
        abg_total_residue_nitrogen_content(products),
        discarded_total_residue_nitrogen_content(products)
    ])

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_complete=term_type_complete,
                    left_on_field_residue=left_on_field_residue,
                    total_nitrogenContent=total_nitrogenContent)

    should_run = any([term_type_complete, left_on_field_residue > 0 and total_nitrogenContent >= 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, left_on_field_residue, total_nitrogenContent


def run(cycle: dict):
    should_run, left_on_field_residue, total_nitrogenContent = _should_run(cycle)
    return _run(cycle, left_on_field_residue, total_nitrogenContent) if should_run else []
