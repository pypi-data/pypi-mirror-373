from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "management": [{"@type": "Management", "methodClassification": "", "methodClassificationDescription": ""}]
    }
}
RETURNS = {
    "The methodClassification as a `string`": ""
}
MODEL_KEY = 'defaultMethodClassificationDescription'


def _should_run(site: dict):
    has_management = bool(site.get('management', []))
    methodClassificationDescription = next((
        n.get('methodClassificationDescription')
        for n in site.get('management', [])
        if n.get('methodClassification')
    ), None) or 'Data calculated by merging real land use histories and modelled land use histories for each Site.'

    logRequirements(site, model=MODEL, model_key=MODEL_KEY,
                    has_management=has_management,
                    methodClassificationDescription=methodClassificationDescription)

    should_run = all([has_management, methodClassificationDescription])
    logShouldRun(site, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run, methodClassificationDescription


def run(site: dict):
    should_run, value = _should_run(site)
    return value
