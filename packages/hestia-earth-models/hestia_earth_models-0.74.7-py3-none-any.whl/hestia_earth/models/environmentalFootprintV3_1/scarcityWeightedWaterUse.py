from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.impact_assessment import impact_country_value
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator",
                                  "term.@id": "freshwaterWithdrawalsDuringCycle",
                                  "value": ""
                                  }],
        "optional": {"country": {"@type": "Term", "termType": "region"}}
    }
}

LOOKUPS = {
    "region-resourceUse-environmentalFootprintV31WaterUse": ""
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}
TERM_ID = 'scarcityWeightedWaterUse'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def run(impact_assessment: dict):
    value = impact_country_value(MODEL, TERM_ID, impact_assessment, f"{list(LOOKUPS.keys())[0]}.csv",
                                 default_world_value=True)
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, value is not None)
    return None if value is None else _indicator(value)
