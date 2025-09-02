from typing import Tuple

from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.landCover import get_pef_grouping
from hestia_earth.models.utils.lookup import _node_value, get_region_lookup_value
from . import MODEL
from ..utils.impact_assessment import get_country_id

REQUIREMENTS = {
    "ImpactAssessment": {
        "optional": {"country": {"@type": "Term", "termType": "region"}},
        "emissionsResourceUse": [{
            "@type": "Indicator",
            "value": ">=0",
            "term.@id": ["landOccupationInputsProduction", "landOccupationDuringCycle"],
            "term.units": "m2*year",
            "landCover": {"@type": "Term", "term.termType": "landCover"}
        }]
    }
}

LOOKUPS = {
    "@doc": "Performs lookup on landCover.csv for column headers and region-pefTermGrouping-landOccupation.csv for CFs",
    "region-pefTermGrouping-landOccupation": "",
    "landCover": "pefTermGrouping"
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}
TERM_ID = 'soilQualityIndexLandOccupation'
LOOKUP = f"{list(LOOKUPS.keys())[1]}.csv"

authorised_indicators = ["landOccupationInputsProduction", "landOccupationDuringCycle"]


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _run(land_occupation_indicators: list):
    values = [indicator['coefficient'] * indicator['area-by-year'] for indicator in land_occupation_indicators]
    return _indicator(list_sum(values))


def _should_run(impact_assessment: dict) -> Tuple[bool, list]:
    land_occupation_indicators = [
        i for i in filter_list_term_type(impact_assessment.get('emissionsResourceUse', []), TermTermType.RESOURCEUSE) if
        i.get('landCover', {}).get('termType') == TermTermType.LANDCOVER.value and
        i.get('term', {}).get('@id', '') in authorised_indicators
    ]

    found_land_occupation_indicators = [{
        'indicator-id': indicator.get('term', {}).get('@id', ''),
        'area-by-year': _node_value(indicator),
        'area-unit': indicator.get('term', {}).get("units"),
        'land-cover-id': indicator.get('landCover', {}).get("@id"),
        'country-id': get_country_id(impact_assessment, blank_node=indicator),
        'area-by-year-is-valid': _node_value(indicator) is not None and _node_value(
            indicator) >= 0,
        'area-unit-is-valid': indicator.get('term', {}).get("units") == "m2*year",
        'pef-grouping': get_pef_grouping(indicator.get('landCover', {}).get("@id"))

    } for indicator in land_occupation_indicators]

    found_indicators_with_coefficient = [
        indicator | {
            'coefficient': get_region_lookup_value(
                model=MODEL,
                term=TERM_ID,
                lookup_name=LOOKUP,
                term_id=indicator['country-id'],
                column=indicator['pef-grouping'],
                fallback_world=True
            )
        } for indicator in found_land_occupation_indicators
    ]

    has_valid_land_occupations = all(
        [
            indicator['area-by-year-is-valid'] and indicator['area-unit-is-valid']
            for indicator in found_land_occupation_indicators
        ]) if found_land_occupation_indicators else False

    valid_indicator_with_coef = [indicator for indicator in found_indicators_with_coefficient if
                                 indicator['coefficient'] is not None and
                                 indicator['area-by-year-is-valid'] and
                                 indicator['area-unit-is-valid']]

    has_land_occupation_indicators = bool(land_occupation_indicators)

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_land_occupation_indicators=has_land_occupation_indicators,
                    has_valid_land_occupations=has_valid_land_occupations,
                    land_occupation_indicators=log_as_table(found_indicators_with_coefficient)
                    )

    should_run = has_land_occupation_indicators and has_valid_land_occupations

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_indicator_with_coef


def run(impact_assessment: dict):
    should_run, land_occupation_indicators = _should_run(impact_assessment)
    return _run(land_occupation_indicators) if should_run else None
