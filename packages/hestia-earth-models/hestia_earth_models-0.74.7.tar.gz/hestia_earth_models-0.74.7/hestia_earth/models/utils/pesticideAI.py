from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from .blank_node import get_inputs_from_properties
from .impact_assessment import convert_value_from_cycle, get_product
from .cycle import impact_lookup_value as cycle_lookup_value


def get_pesticides_from_inputs(cycle: dict):
    inputs = flatten(cycle.get('inputs', []) + [a.get('inputs', []) for a in cycle.get('animals', [])])
    inputs = filter_list_term_type(inputs, TermTermType.PESTICIDEBRANDNAME)
    return flatten([get_inputs_from_properties(i, TermTermType.PESTICIDEAI) for i in inputs])


def impact_lookup_value(model: str, term_id: str, impact_assessment: dict, lookup_col: str):
    cycle = impact_assessment.get('cycle', {})
    is_complete = cycle.get('completeness', {}).get('pesticideVeterinaryDrug', False)
    product = get_product(impact_assessment)
    pesticides = filter_list_term_type(cycle.get('inputs', []), TermTermType.PESTICIDEAI) + \
        get_pesticides_from_inputs(cycle)
    has_pesticides_inputs = len(pesticides) > 0
    pesticides_total_value = convert_value_from_cycle(
        log_node=impact_assessment,
        product=product,
        value=cycle_lookup_value(model, term_id, cycle, pesticides, lookup_col),
        default=None,
        model=model,
        term_id=term_id
    ) if has_pesticides_inputs else 0

    logRequirements(impact_assessment, model=model, term=term_id,
                    lookup_col=lookup_col,
                    term_type_pesticideVeterinaryDrug_complete=is_complete,
                    has_pesticides_inputs=has_pesticides_inputs,
                    impact_value_from_pesticide_ais=pesticides_total_value)

    should_run = is_complete and any([
        len(pesticides) == 0,
        pesticides_total_value is not None
    ])
    logShouldRun(impact_assessment, model, term_id, should_run)

    return pesticides_total_value if should_run else None
