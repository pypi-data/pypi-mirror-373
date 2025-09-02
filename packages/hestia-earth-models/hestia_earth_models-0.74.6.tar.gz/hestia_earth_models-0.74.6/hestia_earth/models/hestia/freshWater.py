from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {"@type": "Measurement", "term.@id": "waterSalinity", "value": "< 500"}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "100",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'freshWater'


def _measurement():
    data = _new_measurement(TERM_ID, MODEL)
    data['value'] = [True]
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data


def _should_run(site: dict):
    waterSalinity = measurement_value(find_term_match(site.get('measurements', []), 'waterSalinity'))

    logRequirements(site, model=MODEL, term=TERM_ID,
                    waterSalinity=waterSalinity)

    should_run = all([0 < (waterSalinity or 0) < 500])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict):
    return _measurement() if _should_run(site) else None
