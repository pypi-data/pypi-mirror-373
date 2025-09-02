from hestia_earth.schema import MeasurementMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement, total_other_soilType_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [{
            "@type": "Measurement",
            "value": "100",
            "depthUpper": "0",
            "depthLower": "30",
            "term.termType": "soilType"
        }]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "0",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": "modelled using other measurements"
    }]
}
LOOKUPS = {
    "soilType": "sumMax100Group"
}
TERM_ID = 'histosol'


def _measurement():
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [0]
    measurement['depthUpper'] = 0
    measurement['depthLower'] = 30
    measurement['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return measurement


def _should_run(site: dict):
    total_measurements_value = total_other_soilType_value(site.get('measurements', []), TERM_ID)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    total_soilType_measurements_value=total_measurements_value,
                    total_soilType_measurements_value_is_100=total_measurements_value == 100)

    should_run = all([total_measurements_value == 100])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return [_measurement()] if _should_run(site) else []
