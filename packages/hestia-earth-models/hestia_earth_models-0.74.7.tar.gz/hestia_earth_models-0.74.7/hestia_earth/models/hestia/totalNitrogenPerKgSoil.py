from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [{"@type": "Measurement", "value": "", "term.@id": "organicCarbonPerKgSoil"}]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "0",
        "depthLower": "50",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'totalNitrogenPerKgSoil'
BIBLIO_TITLE = 'Reducing food’s environmental impacts through producers and consumers'


def _measurement(site: dict, value: float):
    data = _new_measurement(TERM_ID, MODEL)
    data['value'] = [value]
    data['depthUpper'] = 0
    data['depthLower'] = 50
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data | get_source(site, BIBLIO_TITLE)


def _run(site: dict, carbon_content: float):
    value = 0.0000601 * (carbon_content / 1000 * 5000 * 1300) / 11
    return [_measurement(site, value)]


def _should_run(site: dict):
    carbon_content = find_term_match(site.get('measurements', []), 'organicCarbonPerKgSoil')
    carbon_content_value = measurement_value(carbon_content)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    carbon_content_value=carbon_content_value)

    should_run = all([not is_from_model(carbon_content), (carbon_content_value or 0) > 0])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, carbon_content_value


def run(site: dict):
    should_run, carbon_content = _should_run(site)
    return _run(site, carbon_content) if should_run else []
