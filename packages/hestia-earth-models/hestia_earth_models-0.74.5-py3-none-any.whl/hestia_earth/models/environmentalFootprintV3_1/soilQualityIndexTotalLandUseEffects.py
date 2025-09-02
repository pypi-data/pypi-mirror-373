from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL
from ..utils.indicator import _new_indicator

REQUIREMENTS = {
    "ImpactAssessment": {
        "impacts": [
            {"@type": "Indicator", "value": "", "term.@id": "soilQualityIndexLandOccupation"},
            {"@type": "Indicator", "value": "", "term.@id": "soilQualityIndexLandTransformation"}
        ]
    }
}

RETURNS = {
    "Indicator": {
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }
}
TERM_ID = 'soilQualityIndexTotalLandUseEffects'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator["value"] = value
    return indicator


def _run(indicators: list):
    values = [indicator["value"] for indicator in indicators]
    return _indicator(list_sum(values))


def _should_run(impactassessment: dict) -> tuple[bool, list]:
    soil_quality_indicators = [
        i for i in filter_list_term_type(impactassessment.get("impacts", []), TermTermType.CHARACTERISEDINDICATOR) if
        i.get("term", {}).get("@id", "") in ["soilQualityIndexLandOccupation", "soilQualityIndexLandTransformation"]
    ]
    has_soil_quality_indicators = bool(soil_quality_indicators)

    soil_quality_occupation_indicator = find_term_match(soil_quality_indicators, "soilQualityIndexLandOccupation",
                                                        default_val=None)
    has_soil_quality_land_occupation_indicator = bool(soil_quality_occupation_indicator)

    soil_quality_transformation_indicator = find_term_match(soil_quality_indicators,
                                                            "soilQualityIndexLandTransformation",
                                                            default_val=None)
    has_soil_quality_land_transformation_indicator = bool(soil_quality_transformation_indicator)

    has_valid_values = all(
        [isinstance(indicator.get('value', None), (int, float)) for indicator in soil_quality_indicators])

    logRequirements(impactassessment, model=MODEL, term=TERM_ID,
                    has_soil_quality_indicators=has_soil_quality_indicators,
                    has_soil_quality_land_occupation_indicator=has_soil_quality_land_occupation_indicator,
                    has_soil_quality_land_transformation_indicator=has_soil_quality_land_transformation_indicator,
                    has_valid_values=has_valid_values
                    )

    should_run = all([has_soil_quality_indicators, has_valid_values,
                      has_soil_quality_land_occupation_indicator, has_soil_quality_land_transformation_indicator])

    logShouldRun(impactassessment, MODEL, TERM_ID, should_run)
    return should_run, soil_quality_indicators


def run(impactassessment: dict):
    should_run, indicators = _should_run(impactassessment)
    return _run(indicators) if should_run else None
