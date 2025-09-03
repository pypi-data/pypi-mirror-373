from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.cropResidue import sum_above_ground_crop_residue
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": [{
            "@type": "Product",
            "value": "> 0",
            "term.@id": [
                "aboveGroundCropResidueRemoved",
                "aboveGroundCropResidueIncorporated",
                "aboveGroundCropResidueBurnt",
                "aboveGroundCropResidueLeftOnField"
            ]
        }]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'


def _product(value: float):
    product = _new_product(TERM_ID, value)
    return product


def _should_run(cycle: dict):
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)
    value = sum_above_ground_crop_residue(cycle)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_incomplete=term_type_incomplete,
                    sum_above_ground_crop_residue=value)

    should_run = all([term_type_incomplete, value > 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, value


def run(cycle: dict):
    should_run, value = _should_run(cycle)
    return [_product(value)] if should_run else []
