from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_flooded_pre_season_terms
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "none": {
            "practices": [{
                "@type": "Practice",
                "term.termType": "landUseManagement",
                "term.@id": [
                    "nonFloodedPreSeasonLessThan180Days",
                    "nonFloodedPreSeasonMoreThan180Days",
                    "nonFloodedPreSeasonMoreThan365Days",
                    "floodedPreSeasonMoreThan30Days"
                ]
            }]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": "100"
    }]
}
TERM_ID = 'unknownPreSeasonWaterRegime'


def _practice():
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [100]
    return practice


def _should_run(cycle: dict):
    practices = cycle.get('practices', [])
    flooded_terms = get_flooded_pre_season_terms()
    existing_practice = next((p for p in practices if p.get('term', {}).get('@id') in flooded_terms), None)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    existing_practice=existing_practice)

    should_run = all([not existing_practice])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict):
    return [_practice()] if _should_run(cycle) else []
