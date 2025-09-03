from hestia_earth.schema import MeasurementStatsDefinition, MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.source import get_source
from . import MODEL
from .utils import copy_measurement, _value_func

REQUIREMENTS = {
    "Site": {
        "measurements": [{"@type": "Measurement", "value": "", "term.@id": "organicMatterPerM3Soil"}]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "min": "",
        "max": "",
        "statsDefinition": "modelled",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'organicCarbonPerM3Soil'
BIBLIO_TITLE = 'A critical review of the conventional SOC to SOM conversion factor'
FROM_TERM_ID = 'organicMatterPerM3Soil'


def _measurement(site: dict, measurement: dict):
    data = copy_measurement(TERM_ID, measurement)
    data['value'] = _value_func(measurement, lambda v: v / 2)
    data['min'] = _value_func(measurement, lambda v: v / 2.5, 'min')
    data['max'] = _value_func(measurement, lambda v: v / 1.4, 'max')
    data['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data | get_source(site, BIBLIO_TITLE)


def _should_run(site: dict):
    measurement = find_term_match(site.get('measurements', []), FROM_TERM_ID)
    has_matter_measurement = len(measurement.get('value', [])) > 0

    logRequirements(site, model=MODEL, term=TERM_ID,
                    has_matter_measurement=has_matter_measurement)

    should_run = all([has_matter_measurement])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, measurement


def run(site: dict):
    should_run, measurement = _should_run(site)
    return [_measurement(site, measurement)] if should_run else []
