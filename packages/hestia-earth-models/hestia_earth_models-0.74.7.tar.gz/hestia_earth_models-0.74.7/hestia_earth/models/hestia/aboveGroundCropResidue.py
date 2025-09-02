from functools import reduce
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import flatten, list_sum, list_average

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils.cropResidue import PRODUCT_ID_TO_PRACTICES_ID
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "practices": [{
            "@type": "Practice",
            "term.@id": [
                "residueRemoved",
                "residueIncorporated",
                "residueIncorporatedLessThan30DaysBeforeCultivation",
                "residueIncorporatedMoreThan30DaysBeforeCultivation",
                "residueBurnt"
            ]
        }]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
MODEL_KEY = 'aboveGroundCropResidue'
TERM_ID = 'aboveGroundCropResidueLeftOnField,aboveGroundCropResidueBurnt,aboveGroundCropResidueIncorporated,aboveGroundCropResidueRemoved'  # noqa: E501
TOTAL_TERM_ID = 'aboveGroundCropResidueTotal'
REMAINING_MODEL = PRODUCT_ID_TO_PRACTICES_ID[-1]['product']


def _product(term_id: str, value: float):
    return _new_product(term_id, round(value, 7), MODEL)


def _get_practices(term_id: str):
    return flatten([
        model.get('practices', []) for model in PRODUCT_ID_TO_PRACTICES_ID if all([
            model.get('product') == term_id,
            model.get('product') != REMAINING_MODEL
        ])
    ])


def _get_practice_value(term_ids: list, cycle: dict) -> float:
    # multiple practices starting with the `@id` might be present, group together
    values = flatten([
        p.get('value', []) for p in cycle.get('practices', []) if p.get('term', {}).get('@id') in term_ids
    ])
    return list_sum(values) / 100 if len(values) > 0 else None


def _should_run_model(model, cycle: dict, total_value: float):
    term_id = model.get('product')
    practice_value = _get_practice_value(model.get('practices'), cycle)
    has_product = find_term_match(cycle.get('products', []), term_id, None) is not None

    logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                    practice_value=practice_value,
                    has_product=has_product)

    should_run = all([
        any([
            practice_value == 0,
            practice_value is not None and total_value > 0
        ]),
        not has_product
    ])
    logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)
    return should_run, practice_value


def _run_model(model, cycle: dict, total_value: float):
    should_run, practice_value = _should_run_model(model, cycle, total_value)
    return total_value * practice_value if should_run else None


def _model_value(term_id: str, products: list):
    values = find_term_match(products, term_id).get('value', [])
    return list_average(values) if len(values) > 0 else 0


def _remaining_model_value(products: list):
    return list_sum(find_term_match(products, REMAINING_MODEL).get('value', []), 0)


def _run(cycle: dict, total_values: list):
    products = cycle.get('products', [])
    total_value = list_average(total_values)
    # first, calculate the remaining value available after applying all user-uploaded data
    remaining_value = reduce(
        lambda prev, model: prev - _model_value(model.get('product'), products),
        PRODUCT_ID_TO_PRACTICES_ID,
        total_value
    )

    values = []
    # then run every model in order up to the remaining value
    models = [model for model in PRODUCT_ID_TO_PRACTICES_ID if model.get('product') != REMAINING_MODEL]
    for model in models:
        term_id = model.get('product')
        value = _run_model(model, cycle, total_value)
        debugValues(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                    total_above_ground_crop_residue=total_value,
                    remaining_crop_residue_value=remaining_value,
                    allocated_value=value)

        if value == 0:
            values.extend([_product(term_id, value)])
        elif remaining_value > 0 and value is not None and value >= 0:
            value = value if value < remaining_value else remaining_value
            values.extend([_product(term_id, value)])
            remaining_value = remaining_value - value
            if remaining_value == 0:
                break

    return values + [
        # whatever remains is "left on field"
        _product(REMAINING_MODEL, remaining_value + _remaining_model_value(products))
    ] if remaining_value > 0 else values


def _should_run_product(cycle: dict, total_values: list, term_id: str):
    term_type_incomplete = _is_term_type_incomplete(cycle, TOTAL_TERM_ID)
    has_aboveGroundCropResidueTotal = len(total_values) > 0
    practice_term_ids = _get_practices(term_id)
    is_value_0 = any([
        find_term_match(cycle.get('practices', []), term_id).get('value', []) == [0] for term_id in practice_term_ids
    ])

    logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                    term_type_cropResidue_incomplete=term_type_incomplete,
                    has_aboveGroundCropResidueTotal=has_aboveGroundCropResidueTotal,
                    practice_term_ids=';'.join(practice_term_ids),
                    practice_value_is_0=is_value_0)
    should_run = all([has_aboveGroundCropResidueTotal or is_value_0, term_type_incomplete])
    logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)
    return should_run


def _should_run(cycle: dict):
    total_values = find_term_match(cycle.get('products', []), TOTAL_TERM_ID).get('value', [])
    return any([
        _should_run_product(cycle, total_values, term_id) for term_id in TERM_ID.split(',')
    ]), total_values


def run(cycle: dict):
    should_run, total_values = _should_run(cycle)
    return _run(cycle, total_values) if should_run else []
