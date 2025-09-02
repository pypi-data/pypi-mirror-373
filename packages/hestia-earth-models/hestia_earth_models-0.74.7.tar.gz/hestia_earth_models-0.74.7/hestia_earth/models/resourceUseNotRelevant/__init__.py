from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, lookup_term_ids
from hestia_earth.utils.lookup_utils import is_in_system_boundary

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.blank_node import _run_required
from hestia_earth.models.utils.impact_assessment import get_site
from hestia_earth.models.utils.site import get_land_cover_term_id

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator"}]
    }
}
RETURNS = {
    "Indicator": [{
        "value": "0"
    }]
}
LOOKUPS = {
    "resourceUse": [
        "term.id",
        "inHestiaDefaultSystemBoundary",
        "siteTypesAllowed"
    ]
}
MODEL = 'resourceUseNotRelevant'


def _indicator(term_id: str, land_cover_id: str):
    indicator = _new_indicator(term_id, MODEL, land_cover_id)
    indicator['value'] = 0
    return indicator


def _resourceUse_ids():
    return lookup_term_ids(download_lookup(f"{TermTermType.RESOURCEUSE.value}.csv"))


def _should_run_resourceUse(impact: dict):
    def run(term_id: str):
        is_not_relevant = not _run_required(MODEL, term_id, impact.get('cycle', {}))
        in_system_boundary = is_in_system_boundary(term_id)

        should_run = all([is_not_relevant, in_system_boundary])
        if should_run:
            # no need to show the model failed
            logRequirements(impact, model=MODEL, term=term_id,
                            is_not_relevant=is_not_relevant,
                            in_system_boundary=in_system_boundary,
                            run_required=False)
            logShouldRun(impact, MODEL, term_id, should_run)
        return should_run
    return run


def run(_, impact: dict):
    term_ids = _resourceUse_ids()
    term_ids = list(filter(_should_run_resourceUse(impact), term_ids))
    land_cover_term_id = get_land_cover_term_id(get_site(impact).get('siteType'))
    return [_indicator(term_id, land_cover_term_id) for term_id in term_ids]
