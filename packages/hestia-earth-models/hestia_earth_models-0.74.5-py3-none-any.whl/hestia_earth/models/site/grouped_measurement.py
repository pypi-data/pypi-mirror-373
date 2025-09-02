from functools import reduce
from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import non_empty_list, flatten, is_number, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _include
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {"@type": "Measurement", "depthUpper": "", "depthLower": "", "value": ""}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "0",
        "depthUpper": "",
        "depthLower": "",
        "dates": "",
        "methodClassification": "modelled using other measurements"
    }]
}
LOOKUPS = {
    "measurement": ["sumIs100Group", "sumMax100Group"]
}
MODEL_KEY = 'grouped_measurement'


def _measurement(term_id: str, measurement: dict):
    data = _new_measurement(term_id) | _include(measurement, [
        'depthUpper', 'depthLower', 'startDate', 'endDate', 'dates'
    ])
    data["value"] = [0]
    data["methodClassification"] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data


def _measurement_term_ids(measurements: list):
    return list(set([m.get('term', {}).get('@id') for m in measurements]))


def _formatDepth(depth: str):
    # handle float values
    return str(int(depth)) if is_number(depth) else ''


def _group_by_depth(measurements: list):
    def group_by(group: dict, measurement: dict):
        keys = non_empty_list([
            _formatDepth(measurement.get('depthUpper')),
            _formatDepth(measurement.get('depthLower'))
        ])
        key = '-'.join(keys) if len(keys) > 0 else 'default'
        group[key] = group.get(key, []) + [measurement]
        return group

    return reduce(group_by, measurements, {})


def _run_measurements(site: dict, all_term_ids: list, measurements: list):
    term_ids = _measurement_term_ids(measurements)

    # check the total value is 100%
    total_value = list_sum([
        list_sum(m.get('value')) for m in measurements
    ])
    is_total_100 = 99.5 <= total_value <= 100.5

    should_run = all([is_total_100])

    other_term_ids = [v for v in all_term_ids if v not in term_ids]
    for term_id in other_term_ids:
        logRequirements(site, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        total_value=total_value)

        logShouldRun(site, MODEL, term_id, should_run, model_key=MODEL_KEY)

    return [
        _measurement(term_id=term_id, measurement=measurements[0])
        for term_id in other_term_ids
    ] if should_run else []


def _run(site: dict, measurements: list):
    term_ids = _measurement_term_ids(measurements)
    grouped_measurements = _group_by_depth(measurements)

    return flatten([
        _run_measurements(site, term_ids, values)
        for values in grouped_measurements.values()
    ]) if len(grouped_measurements.keys()) > 1 else []


def _group_by_100group(measurements: list):
    def group_by(group: dict, measurement: dict):
        term = measurement.get('term', {})
        sum_group_key = (
            get_lookup_value(term, 'sumIs100Group', skip_debug=True, model=MODEL) or
            get_lookup_value(term, 'sumMax100Group', skip_debug=True, model=MODEL)
        )
        keys = non_empty_list([
            sum_group_key,
            measurement.get('startDate'),
            measurement.get('endDate'),
            '-'.join(measurement.get('dates') or []),
        ])
        key = '-'.join(keys) if len(keys) > 0 else 'default'

        if all([
            sum_group_key,
            measurement.get('value', []),
            measurement.get('depthUpper') is not None,
            measurement.get('depthLower') is not None
        ]):
            group[key] = group.get(key, []) + [measurement]

        return group

    return reduce(group_by, measurements, {})


def run(site: dict):
    grouped_measurements = _group_by_100group(site.get('measurements', []))
    return flatten([
        _run(site, values)
        for values in grouped_measurements.values()
        if len(values) > 1
    ])
