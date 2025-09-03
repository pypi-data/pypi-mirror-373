from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import impact_emission_lookup_value
from hestia_earth.models.utils.pesticideAI import impact_lookup_value as pesticides_lookup_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "emission"}],
        "cycle": {
            "@type": "Cycle",
            "completeness.pesticideVeterinaryDrug": "True",
            "inputs": [{"@type": "Input", "value": "", "term.termType": "pesticideAI"}]
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "emission": "noxEqHierarchistEcosystemDamageOzoneFormationReCiPe2016",
    "pesticideAI": "noxEqHierarchistEcosystemDamageOzoneFormationReCiPe2016"
}
TERM_ID = 'ecosystemDamageOzoneFormation'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def run(impact_assessment: dict):
    emissions_value = impact_emission_lookup_value(MODEL, TERM_ID, impact_assessment, LOOKUPS['emission'])
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    emissions_value=emissions_value)

    pesticides_value = pesticides_lookup_value(MODEL, TERM_ID, impact_assessment, LOOKUPS['pesticideAI'])

    value = sum_values([emissions_value, pesticides_value])

    should_run = all([value is not None])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return _indicator(value) if should_run else None
