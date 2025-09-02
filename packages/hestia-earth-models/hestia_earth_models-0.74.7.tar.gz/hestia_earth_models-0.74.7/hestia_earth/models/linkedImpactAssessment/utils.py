from hestia_earth.utils.tools import non_empty_list, flatten, list_sum

from hestia_earth.models.log import log_as_table, debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import group_by, sum_values, _include
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, convert_value_from_cycle
from hestia_earth.models.utils.input import load_impacts
from . import MODEL


def _indicator(model: str, term_id: str, value: float, input: dict):
    indicator = _new_indicator(term_id, model)
    indicator['value'] = value
    indicator['inputs'] = [input]
    return indicator


def _run_indicators(impact_assessment: dict, product: dict, term_id: str, model: str):
    def run(values: list):
        input = values[0].get('input').get('term', {})
        indicator = values[0].get('indicator')
        values_from_cycle = non_empty_list([
            list_sum(value.get('input').get('value')) * value.get('indicator').get('value')
            for value in values
        ])
        value = convert_value_from_cycle(
            impact_assessment, product, sum_values(values_from_cycle), model=model, term_id=term_id
        )

        # show values per input in the logs
        debugValues(impact_assessment, model=model, term=term_id,
                    value=value,
                    coefficient=1,
                    input=input.get('@id'))

        return (
            _indicator(model, term_id, value, input) | _include(indicator, ['landCover', 'previousLandCover'])
        ) if value is not None else None
    return run


def _run_inputs_production(impact_assessment: dict, product: dict, term_id: str, model: str):
    cycle = impact_assessment.get('cycle', {})

    inputs = load_impacts(cycle.get('inputs', []))
    inputs_with_impact = [i for i in inputs if i.get('impactAssessment')]

    # group all indicators per `landCover` and `previousLandCover`
    all_indicators = flatten([
        {
            'indicator': indicator,
            'input': input
        }
        for input in inputs
        for indicator in (
            input.get('impactAssessment', {}).get('emissionsResourceUse', []) +
            input.get('impactAssessment', {}).get('impacts', [])
        )
        if indicator.get('term', {}).get('@id') in [
            term_id,
            term_id.replace('InputsProduction', 'DuringCycle')
        ]
    ])
    valid_indicators = [
        value
        for value in all_indicators
        if all([
            (value.get('indicator').get('value') or -1) > 0,
            (list_sum(value.get('input').get('value')) or -1) > 0
        ])
    ]
    grouped_indicators = group_by(valid_indicators, [
        'input.term.@id', 'indicator.landCover.@id', 'indicator.previousLandCover.@id'
    ])
    has_indicators = bool(valid_indicators)

    logRequirements(impact_assessment, model=model, term=term_id,
                    inputs_with_linked_impact_assessment=len(inputs_with_impact),
                    indicators=log_as_table([
                        {
                            'indicator-id': value.get('indicator').get('term', {}).get('@id'),
                            'indicator-value': value.get('indicator').get('value'),
                            'input-id': value.get('input').get('term', {}).get('@id'),
                            'input-value': list_sum(value.get('input').get('value')),
                        }
                        for value in all_indicators
                    ]))

    should_run = all([has_indicators])
    logShouldRun(impact_assessment, model, term_id, should_run)

    return non_empty_list(flatten(
        map(_run_indicators(impact_assessment, product, term_id, model), grouped_indicators.values())
    ))


def _should_run_inputs_production(impact_assessment: dict, term_id: str, model: str):
    product = get_product(impact_assessment) or {}
    product_id = product.get('term', {}).get('@id')

    product_value = list_sum(product.get('value', []), default=None)
    economic_value = product.get('economicValueShare')

    logRequirements(impact_assessment, model=model, term=term_id,
                    product_id=product_id,
                    product_value=product_value,
                    product_economicValueShare=economic_value)

    should_run = all([product, product_value, economic_value])
    logShouldRun(impact_assessment, model, term_id, should_run)
    return should_run, product


def run_inputs_production(impact_assessment: dict, term_id: str, model: str = MODEL):
    should_run, product = _should_run_inputs_production(impact_assessment, term_id, model)
    return _run_inputs_production(impact_assessment, product, term_id, model) if should_run else []
