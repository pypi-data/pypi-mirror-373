from typing import List, Tuple

from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.impact_assessment import get_country_id
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.landCover import get_pef_grouping
from hestia_earth.models.utils.lookup import _node_value, get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [
            {
                "@type": "Indicator",
                "term.termType": "resourceUse",
                "term.@id": "landTransformation20YearAverageDuringCycle",
                "value": ">= 0",
                "landCover": {"@type": "Term", "term.termType": "landCover"},
                "previousLandCover": {"@type": "Term", "term.termType": "landCover"}
            }
        ],
        "optional": {
            "country": {"@type": "Term", "termType": "region"},
            "emissionsResourceUse": [
                {
                    "@type": "Indicator",
                    "term.termType": "resourceUse",
                    "term.@id": "landTransformation20YearAverageInputsProduction",
                    "value": ">= 0",
                    "landCover": {"@type": "Term", "term.termType": "landCover"},
                    "previousLandCover": {"@type": "Term", "term.termType": "landCover"}
                }
            ]
        }
    }
}

# Note: CFs in `region-pefTermGrouping-landTransformation-from.csv` appear to be the opposite values as those in
# `region-pefTermGrouping-landTransformation-to.csv` but can be different in some cases.
LOOKUPS = {
    "region-pefTermGrouping-landTransformation-from": "",
    "region-pefTermGrouping-landTransformation-to": "",
    "landCover": "pefTermGrouping"
}

from_lookup_file = f"{list(LOOKUPS.keys())[0]}.csv"
to_lookup_file = f"{list(LOOKUPS.keys())[1]}.csv"

LOOKUP = {
    "from": from_lookup_file,
    "to": to_lookup_file
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}

TERM_ID = 'soilQualityIndexLandTransformation'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _run(transformations: List[dict]):
    values = [
        (transformation.get("factor-from", 0) + transformation.get("factor-to", 0)
         ) * transformation.get("value", 0) * 20
        for transformation in transformations
    ]
    return _indicator(list_sum(values))


def _is_valid_indicator(indicator: dict) -> bool:
    return indicator['term']['@id'] in ["landTransformation20YearAverageInputsProduction",
                                        "landTransformation20YearAverageDuringCycle"]


def _should_run(impact_assessment: dict) -> Tuple[bool, list]:
    resource_uses = [
        i for i in filter_list_term_type(impact_assessment.get('emissionsResourceUse', []), TermTermType.RESOURCEUSE) if
        _is_valid_indicator(i)
    ]

    found_transformations = [
        {
            'indicator-id': indicator.get('term', {}).get('@id', ''),
            'value': _node_value(indicator),
            'land-cover-id-from': indicator.get('previousLandCover', {}).get("@id"),
            'land-cover-id-to': indicator.get('landCover', {}).get("@id"),
            'good-land-cover-term': all([
                bool(indicator.get('landCover')),
                bool(indicator.get('previousLandCover'))
            ]),
            'country-id': get_country_id(impact_assessment, blank_node=indicator),
            'value-is-valid': (
                _node_value(indicator) is not None and
                _node_value(indicator) >= 0
            )
        } for indicator in resource_uses
    ]

    found_transformations_with_coefficient = [
        transformation | {
            'factor-from': get_region_lookup_value(
                model=MODEL,
                term=TERM_ID,
                lookup_name=from_lookup_file,
                term_id=transformation['country-id'],
                column=get_pef_grouping(transformation['land-cover-id-from']),
                fallback_world=True
            ) if transformation['land-cover-id-from'] else None,
            'factor-to': get_region_lookup_value(
                model=MODEL,
                term=TERM_ID,
                lookup_name=to_lookup_file,
                term_id=transformation['country-id'],
                column=get_pef_grouping(transformation['land-cover-id-to']),
                fallback_world=True
            ) if transformation['land-cover-id-to'] else None
        } for transformation in found_transformations
    ]

    valid_transformations_with_coef = [
        t for t in found_transformations_with_coefficient if all([
            t['value-is-valid'],
            t['factor-from'] is not None,
            t['factor-to'] is not None
        ])
    ]

    has_land_transformation_indicators = any([
        _is_valid_indicator(indicator)
        for indicator in resource_uses
    ])

    all_transformations_are_valid = all(
        [
            all([t['value-is-valid'], t['good-land-cover-term']])
            for t in found_transformations_with_coefficient
        ]
    ) if found_transformations_with_coefficient else False

    has_a_during_cycle_indicator = bool(find_term_match(resource_uses, "landTransformation20YearAverageDuringCycle"))

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_land_transformation_indicators=has_land_transformation_indicators,
                    has_a_during_cycle_indicator=has_a_during_cycle_indicator,
                    all_transformations_are_valid=all_transformations_are_valid,
                    has_valid_transformations_with_coef=bool(valid_transformations_with_coef),
                    found_transformations=log_as_table(found_transformations_with_coefficient)
                    )

    should_run = all([has_land_transformation_indicators,
                      has_a_during_cycle_indicator,
                      all_transformations_are_valid])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_transformations_with_coef


def run(impact_assessment: dict):
    should_run, transformations = _should_run(impact_assessment)
    return _run(transformations) if should_run else None
