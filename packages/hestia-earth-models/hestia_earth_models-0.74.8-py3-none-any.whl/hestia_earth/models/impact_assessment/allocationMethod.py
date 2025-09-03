from hestia_earth.schema import ImpactAssessmentAllocationMethod

from hestia_earth.models.log import logShouldRun, logRequirements
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "updated": ["emissionsResourceUse", "impacts", "endpoints"],
        "added": ["emissionsResourceUse", "impacts", "endpoints"]
    }
}
RETURNS = {
    "`economic` if any indicators were updated or added by the HESTIA models": ""
}

MODEL_KEY = 'allocationMethod'
_MODIFIED_KEYS = ["emissionsResourceUse", "impacts", "endpoints"]


def _should_run(impact: dict):
    modified = impact.get('updated', []) + impact.get('added', [])
    is_modified_by_hestia = any([key for key in _MODIFIED_KEYS if key in modified])

    logRequirements(impact, model=MODEL, key=MODEL_KEY,
                    is_modified_by_hestia=is_modified_by_hestia)

    should_run = all([is_modified_by_hestia])
    logShouldRun(impact, MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(impact: dict):
    return ImpactAssessmentAllocationMethod.ECONOMIC.value if _should_run(impact) else None
