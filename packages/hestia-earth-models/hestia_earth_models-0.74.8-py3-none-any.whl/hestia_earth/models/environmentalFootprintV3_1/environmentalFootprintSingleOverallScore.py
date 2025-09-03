from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum
from typing import List, Optional, Tuple

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table, debugValues
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.lookup import _node_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "impacts": [{
            "@type": "Indicator",
            "value": "",
            "term.name": "PEF indicators only"
        }]
    }
}

LOOKUPS = {
    "@doc": "Normalisation factors in PEF v3.1 are calculated using a Global population number of 6,895,889,018",
    "characterisedIndicator": [
        "pefTerm-normalisation-v3_1",
        "pefTerm-weighing-v3_1",
        "pefTerm-methodModel-whiteList-v3-1"
    ]
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}

TERM_ID = 'environmentalFootprintSingleOverallScore'

normalisation_column = LOOKUPS['characterisedIndicator'][0]
weighing_column = LOOKUPS['characterisedIndicator'][1]
method_model_colum = LOOKUPS['characterisedIndicator'][2]


def _is_a_PEF_indicator(indicator: dict) -> bool:
    term = indicator.get('term', {})
    indicator_method_model = indicator.get('methodModel', {}).get("@id")
    return all([
        indicator_method_model,
        indicator_method_model in _get_pef_method_model(term),
        _get_factor(term, normalisation_column) is not None,
        _get_factor(term, weighing_column) is not None
    ])


def _get_factor(term: dict, column: str) -> Optional[float]:
    factor = get_lookup_value(term, column, model=MODEL, term=TERM_ID)
    return float(factor) if factor is not None else None


def _get_pef_method_model(term: dict) -> List[str]:
    entries = get_lookup_value(term, method_model_colum, model=MODEL, term=TERM_ID) or ''
    return entries.split(";")


def _indicator_factors(impact_assessment: dict, indicator: dict):
    value = _node_value(indicator)
    normalisation_factor = _get_factor(indicator.get('term', {}), normalisation_column)
    weighting_factor = _get_factor(indicator.get('term', {}), weighing_column)
    coefficient = 0 if all([
        weighting_factor == 0,
        normalisation_factor == 0
    ]) else (weighting_factor / 100) / normalisation_factor if all([
        weighting_factor is not None,
        normalisation_factor is not None
    ]) else None

    debugValues(impact_assessment, model=MODEL, term=TERM_ID,
                node=indicator['term']['@id'],
                value=value,
                coefficient=coefficient)

    return {
        "value": value,
        "normalisation-used": normalisation_factor,
        "weighting-used": weighting_factor,
        "coefficient": coefficient,
        "weighted-value": value * coefficient if all([value is not None, coefficient is not None]) else None,
    }


def _count_duplicate_indicators(reference_indicator: dict, indicators: list) -> int:
    """
    Counts the number of `reference_indicator` indicators found in a list of indicators.
    Uses indicator.term.@id and indicator.key to determine uniqueness.
    """
    return sum([
        1
        for i in indicators
        if all([
            i["term"]["@id"] == reference_indicator["term"]["@id"],
            i.get("key", {}).get("@id") == reference_indicator.get("key", {}).get("@id")
        ])
    ])


def _indicator(value: float) -> dict:
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _run(indicators: List[dict]):
    return _indicator(value=list_sum([indicator["weighted-value"] for indicator in indicators]))


def _valid_indicator(indicator: Optional[dict]) -> bool:
    value = None if indicator is None else _node_value(indicator)
    return isinstance(value, (int, float)) and _is_a_PEF_indicator(indicator)


def _should_run(impact_assessment: dict) -> Tuple[bool, list[dict]]:
    indicators = [
        indicator for indicator in
        filter_list_term_type(impact_assessment.get('impacts', []), TermTermType.CHARACTERISEDINDICATOR)
        if _is_a_PEF_indicator(indicator)
    ]
    has_pef_indicators = bool(indicators)

    processed_indicators = [{
        "indicator": indicator['term']['@id'],
        "valid-indicator": _valid_indicator(indicator),
        "one-indicator-for-category": _count_duplicate_indicators(indicator, indicators) == 1,
        "indicator-pef-category": indicator.get('term', {}).get('@id'),
    } | _indicator_factors(impact_assessment, indicator) for indicator in indicators]

    no_duplicate_indicators = all([indicator['one-indicator-for-category'] for indicator in processed_indicators])
    valid_indicators = [indicator for indicator in processed_indicators if indicator['valid-indicator']]
    all_indicators_valid = all([indicator['valid-indicator'] for indicator in processed_indicators])

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_pef_indicators=has_pef_indicators,
                    no_duplicate_indicators=no_duplicate_indicators,
                    all_indicators_valid=all_indicators_valid,
                    processed_indicators=log_as_table(processed_indicators),
                    )

    should_run = all([has_pef_indicators, all_indicators_valid, no_duplicate_indicators])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_indicators


def run(impact_assessment: dict):
    should_run, indicators = _should_run(impact_assessment)
    return _run(indicators) if should_run else None
