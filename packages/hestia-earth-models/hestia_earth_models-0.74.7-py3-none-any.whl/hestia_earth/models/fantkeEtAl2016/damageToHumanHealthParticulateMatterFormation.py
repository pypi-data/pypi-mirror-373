from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.impact_assessment import impact_emission_lookup_value
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "emission"}]
    }
}
LOOKUPS = {
    "emission": "damageToHumanHealthParticulateMatterFormationFantkeEtAl2016"
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}

TERM_ID = 'damageToHumanHealthParticulateMatterFormation'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def run(impact_assessment: dict):
    value = impact_emission_lookup_value(
        model=MODEL, term_id=TERM_ID, impact=impact_assessment, lookup_col=LOOKUPS['emission'], group_key='default'
    )
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value)

    should_run = all([value is not None])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return _indicator(value) if should_run else None
