from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils import is_from_model
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "or": {
            "practices": [{
                "@type": "Practice",
                "term.@id": [
                    "residueIncorporated",
                    "residueIncorporatedLessThan30DaysBeforeCultivation",
                    "residueIncorporatedMoreThan30DaysBeforeCultivation"
                ]
            }],
            "products": [
                {"@type": "Product", "term.@id": "aboveGroundCropResidueTotal", "value": "> 0"},
                {"@type": "Product", "term.@id": "aboveGroundCropResidueRemoved", "value": "> 0"}
            ]
        },
        "none": {
            "practices": [{
                "@type": "Practice",
                "term.@id": [
                    "residueRemoved",
                    "residueBurnt",
                    "residueLeftOnField"
                ]
            }]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'residueRemoved'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _run_by_products(cycle: dict):
    products = cycle.get('products', [])
    aboveGroundCropResidueTotal = list_sum(find_term_match(products, 'aboveGroundCropResidueTotal').get('value'))
    aboveGroundCropResidueRemoved = list_sum(find_term_match(products, 'aboveGroundCropResidueRemoved').get('value'))
    return [_practice(aboveGroundCropResidueRemoved / aboveGroundCropResidueTotal * 100)]


def _should_run_by_products(cycle: dict):
    crop_residue_incomplete = _is_term_type_incomplete(cycle, TermTermType.CROPRESIDUE)
    products = cycle.get('products', [])
    aboveGroundCropResidueTotal = list_sum(find_term_match(products, 'aboveGroundCropResidueTotal').get('value', [0]))
    has_aboveGroundCropResidueTotal = aboveGroundCropResidueTotal > 0
    aboveGroundCropResidueRemoved = list_sum(
        find_term_match(products, 'aboveGroundCropResidueRemoved').get('value', [0]))
    has_aboveGroundCropResidueRemoved = aboveGroundCropResidueRemoved > 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_incomplete=crop_residue_incomplete,
                    has_aboveGroundCropResidueTotal=has_aboveGroundCropResidueTotal,
                    has_aboveGroundCropResidueRemoved=has_aboveGroundCropResidueRemoved)

    should_run = all([crop_residue_incomplete, has_aboveGroundCropResidueTotal, has_aboveGroundCropResidueRemoved])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def _is_incorporated_practice(practice: dict):
    return all([
        practice.get('term', {}).get('@id').startswith('residueIncorporated'),
        practice.get('term', {}).get('termType') == TermTermType.CROPRESIDUEMANAGEMENT.value,
        not is_from_model(practice)
    ])


def _run_by_practices(cycle: dict):
    incorporated_value = list_sum([
        list_sum(p.get('value'))
        for p in cycle.get('practices', [])
        if _is_incorporated_practice(p)
    ])
    return [_practice(100 - (incorporated_value or 0))]


def _should_run_by_practices(cycle: dict):
    crop_residue_incomplete = _is_term_type_incomplete(cycle, TermTermType.CROPRESIDUE)

    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    incorporated_practices = [
        {'id': p.get('term', {}).get('@id'), 'value': list_sum(p.get('value'), None)}
        for p in practices
        if _is_incorporated_practice(p)
    ]
    has_other_practices = any([
        not p.get('term', {}).get('@id').startswith('residueIncorporated')
        for p in practices
    ])
    incorporated_value = list_sum([p.get('value') for p in incorporated_practices], None)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_incomplete=crop_residue_incomplete,
                    incorporated_practices=log_as_table(incorporated_practices),
                    incorporated_value=incorporated_value,
                    has_other_practices=has_other_practices)

    should_run = all([crop_residue_incomplete, incorporated_value, not has_other_practices])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict):
    return (
        _run_by_products(cycle) if _should_run_by_products(cycle) else
        _run_by_practices(cycle) if _should_run_by_practices(cycle) else
        []
    )
