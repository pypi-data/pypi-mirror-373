from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from .impact_assessment import convert_value_from_cycle, get_product
from .cycle import impact_lookup_value as cycle_lookup_value


def impact_lookup_value(model: str, term_id: str, impact_assessment: dict, lookup_col: str):
    cycle = impact_assessment.get('cycle', {})
    fuel_complete = cycle.get('completeness', {}).get('electricityFuel', False)
    product = get_product(impact_assessment)
    fuels = filter_list_term_type(cycle.get('inputs', []), TermTermType.FUEL)
    has_fuels_inputs = len(fuels) > 0
    fuels_total_value = convert_value_from_cycle(
        impact_assessment,
        product,
        cycle_lookup_value(model, term_id, cycle, fuels, lookup_col),
        model=model, term_id=term_id
    ) if has_fuels_inputs else None
    logRequirements(impact_assessment, model=model, term=term_id,
                    term_type_electricityFuel_complete=fuel_complete,
                    has_fuels_inputs=has_fuels_inputs,
                    fuels_total_value=fuels_total_value)

    should_run = any([
        fuel_complete and not has_fuels_inputs,
        fuel_complete and fuels_total_value is not None
    ])
    logShouldRun(impact_assessment, model, term_id, should_run)

    return (fuels_total_value or 0) if should_run else None
