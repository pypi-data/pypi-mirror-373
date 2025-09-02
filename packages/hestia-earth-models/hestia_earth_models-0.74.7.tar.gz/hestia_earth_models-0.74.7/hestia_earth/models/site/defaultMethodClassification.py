from hestia_earth.schema import SiteDefaultMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "management": [{"@type": "Management", "methodClassification": ""}]
    }
}
RETURNS = {
    "The methodClassification as a `string`": ""
}
MODEL_KEY = 'defaultMethodClassification'


def _should_run(site: dict):
    has_management = bool(site.get('management', []))
    methodClassification = next(
        (n.get('methodClassification') for n in site.get('management', [])),
        None
    ) or SiteDefaultMethodClassification.MODELLED.value

    logRequirements(site, model=MODEL, model_key=MODEL_KEY,
                    has_management=has_management,
                    methodClassification=methodClassification)

    should_run = all([has_management, methodClassification])
    logShouldRun(site, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run, methodClassification


def run(site: dict):
    should_run, value = _should_run(site)
    return value
