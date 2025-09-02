from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.fuel import impact_lookup_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "completeness.electricityFuel": "True",
            "inputs": [{"@type": "Input", "value": "", "term.termType": "fuel"}]
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "fuel": "oilEqIndividualistFossilResourceScarcityReCiPe2016"
}
TERM_ID = 'fossilResourceScarcity'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def run(impact_assessment: dict):
    value = impact_lookup_value(MODEL, TERM_ID, impact_assessment, LOOKUPS['fuel'])
    return None if value is None else _indicator(value)
