from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": [
            {"@type": "Product", "term.@id": "aboveGroundCropResidueTotal", "value": "> 0"},
            {"@type": "Product", "term.@id": "aboveGroundCropResidueLeftOnField", "value": "> 0"}
        ]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'residueLeftOnField'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _should_run(cycle: dict):
    crop_residue_incomplete = _is_term_type_incomplete(cycle, TermTermType.CROPRESIDUE)
    products = cycle.get('products', [])
    aboveGroundCropResidueTotal = list_sum(find_term_match(products, 'aboveGroundCropResidueTotal').get('value', [0]))
    has_aboveGroundCropResidueTotal = aboveGroundCropResidueTotal > 0
    aboveGroundCropResidueLeftOnField = list_sum(
        find_term_match(products, 'aboveGroundCropResidueLeftOnField').get('value', [0]))
    has_aboveGroundCropResidueLeftOnField = aboveGroundCropResidueLeftOnField > 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_incomplete=crop_residue_incomplete,
                    has_aboveGroundCropResidueTotal=has_aboveGroundCropResidueTotal,
                    has_aboveGroundCropResidueLeftOnField=has_aboveGroundCropResidueLeftOnField)

    should_run = all([crop_residue_incomplete, has_aboveGroundCropResidueTotal, has_aboveGroundCropResidueLeftOnField])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, aboveGroundCropResidueTotal, aboveGroundCropResidueLeftOnField


def run(cycle: dict):
    should_run, total, value = _should_run(cycle)
    return [_practice(value / total * 100)] if should_run else []
