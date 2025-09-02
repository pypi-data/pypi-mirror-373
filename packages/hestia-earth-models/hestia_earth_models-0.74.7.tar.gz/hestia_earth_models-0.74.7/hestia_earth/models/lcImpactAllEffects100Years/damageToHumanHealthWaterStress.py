from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import impact_country_value, impact_aware_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "resourceUse"}],
        "site": {
            "@type": "Site",
            "or": {
                "awareWaterBasinId": "",
                "country": {"@type": "Term", "termType": "region"}
            }
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "@doc": "Different lookup files are used depending on the situation",
    "awareWaterBasinId-resourceUse-WaterStressDamageToHumanHealthLCImpactCF": "",
    "region-resourceUse-WaterStressDamageToHumanHealthLCImpactCF": ""
}
TERM_ID = 'damageToHumanHealthWaterStress'
LOOKUP_SUFFIX = 'resourceUse-WaterStressDamageToHumanHealthLCImpactCF'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def run(impact_assessment: dict):
    value = impact_aware_value(
        MODEL, TERM_ID,
        impact_assessment,
        f"awareWaterBasinId-{LOOKUP_SUFFIX}.csv"
    ) or impact_country_value(
        MODEL, TERM_ID,
        impact_assessment,
        f"region-{LOOKUP_SUFFIX}.csv"
    )
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, value is not None)
    return None if value is None else _indicator(value)
