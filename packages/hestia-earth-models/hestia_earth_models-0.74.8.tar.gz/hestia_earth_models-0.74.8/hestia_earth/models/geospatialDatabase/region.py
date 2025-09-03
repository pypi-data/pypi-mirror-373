from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import linked_node

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from .utils import download, has_coordinates
from hestia_earth.models.utils.term import download_term
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "latitude": "",
        "longitude": ""
    }
}
RETURNS = {
    "Term": {"@type": "Term", "termType": "region"}
}
MODEL_KEY = 'region'
EE_PARAMS = {
    'ee_type': 'vector',
    'collection': 'gadm36_1',
    'fields': 'GID_1'
}


def _download_region(site: dict):
    gadm_id = download(
        MODEL_KEY,
        site,
        EE_PARAMS,
        only_coordinates=True
    )
    try:
        return None if gadm_id is None else linked_node(download_term(f"GADM-{gadm_id}", TermTermType.REGION))
    except Exception:
        return None


def _run(site: dict):
    value = _download_region(site)
    debugValues(site, model=MODEL, key=MODEL_KEY, region_id=value.get('@id') if value else None)
    return value


def _should_run(site: dict):
    contains_coordinates = has_coordinates(site)

    logRequirements(site, model=MODEL, key=MODEL_KEY,
                    contains_coordinates=contains_coordinates)

    should_run = all([contains_coordinates])
    logShouldRun(site, MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
