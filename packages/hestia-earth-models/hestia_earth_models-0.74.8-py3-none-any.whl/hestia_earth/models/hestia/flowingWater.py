from hestia_earth.schema import MeasurementMethodClassification, SiteSiteType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils.site import WATER_TYPES
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "siteType": ["pond", "river or stream", "lake", "sea or ocean"]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "1",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'slowFlowingWater,fastFlowingWater'
BIBLIO_TITLE = 'Reducing food’s environmental impacts through producers and consumers'
SITE_TYPE_TO_TERM_ID = {
    SiteSiteType.RIVER_OR_STREAM.value: 'fastFlowingWater'
}


def _measurement(site: dict, term_id: str):
    data = _new_measurement(term_id, MODEL)
    data['value'] = [True]
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data | get_source(site, BIBLIO_TITLE)


def _run(site: dict):
    site_type = site.get('siteType')
    term_id = SITE_TYPE_TO_TERM_ID.get(site_type, 'slowFlowingWater')
    return _measurement(site, term_id)


def _should_run(site: dict):
    site_type = site.get('siteType')

    logRequirements(site, model=MODEL, term=TERM_ID,
                    site_type=site_type)

    should_run = site_type in WATER_TYPES
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
