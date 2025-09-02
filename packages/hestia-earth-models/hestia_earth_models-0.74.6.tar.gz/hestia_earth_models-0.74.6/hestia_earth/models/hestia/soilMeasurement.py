from collections import defaultdict
from copy import deepcopy
from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.tools import non_empty_list, flatten

from hestia_earth.models.log import logRequirements, logShouldRun, logErrorRun, log_as_table
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
        "value": "",
        "depthUpper": 0,
        "depthLower": [30, 50],
        "dates": "",
        "methodClassification": "modelled using other measurements"
    }]
}
LOOKUPS = {
    "measurement": "depthSensitive"
}
MODEL_KEY = 'soilMeasurement'
STANDARD_DEPTHS = {(0, 30), (0, 50)}


def _measurement(value: float, date: str, term_id: str, standard_fields: dict):
    data = _new_measurement(term_id, MODEL)
    data["value"] = [value]
    data["depthUpper"] = standard_fields["depthUpper"]
    data["depthLower"] = standard_fields["depthLower"]
    data["methodClassification"] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    if date and date[0]:
        data["dates"] = [date]
    return data


def _get_overlap(in_lower: int, in_upper: int, out_lower: int, out_upper: int):
    """Returns the amount of overlap between upper-lower and range_upper-range_lower."""
    if in_lower >= in_upper or out_lower >= out_upper or in_lower >= out_upper or in_upper <= out_lower:
        return 0

    overlap_range = [max(in_lower, out_lower), min(in_upper, out_upper)]
    return max(overlap_range) - min(overlap_range)


def _harmonise_measurements(measurements_list: list, standard_depth_lower: int, standard_depth_upper: int) -> float:
    """Gather measurements and calculate modelled value."""
    total_weight_values = 0
    total_weights = 0
    for measurement_dict in measurements_list:
        value = measurement_dict.get("value", [])[0]
        if value is None:
            continue
        depth_lower = measurement_dict.get("depthLower", 0)
        depth_upper = measurement_dict.get("depthUpper", 0)
        # Note that the upper/lower here is reversed as lower in the ground (greater depth),
        # means higher numbers.
        weight = _get_overlap(
            in_lower=depth_upper,
            in_upper=depth_lower,
            out_lower=standard_depth_upper,
            out_upper=standard_depth_lower
        )
        total_weights += weight
        total_weight_values += value * weight
    modelled_value = total_weight_values / total_weights if total_weights else 0
    return modelled_value


def _expand_multiple_measurements(measurements):
    """Split/expand measurements with arrays of values and dates into distinct measurements."""
    expanded_measurements = []
    for measurement in measurements:
        if "dates" in measurement and len(measurement.get("value", [])) != len(measurement.get("dates", [])):
            logErrorRun(
                model=MODEL,
                term=measurement.get("term", {}),
                error="Inconsistent field lengths between values and dates fields in measurement."
            )
        elif len(measurement.get("value", [])) < 2:
            expanded_measurements.append(measurement)
        else:
            for v, d in zip(measurement.get("value", []), measurement.get("dates", [])):
                new_measurement = deepcopy(measurement)
                new_measurement.update({"value": [v], "dates": [d]})
                expanded_measurements.append(new_measurement)

    return expanded_measurements


def _group_measurements_by_date_method_term(measurements):
    group_by_result = defaultdict(list)
    for measurement_dict in measurements:
        dates = measurement_dict.get("dates", [])
        method = measurement_dict.get("method", {}).get("@id", "")
        term_id = measurement_dict.get("term", {}).get("@id", "")
        if not dates:
            dates = [measurement_dict.get('endDate', "")]
        group_by_result[(dates[0], method, term_id)].append(measurement_dict)
    return group_by_result


def _run_harmonisation(measurements: list) -> list:
    results = []
    grouped_measurements = _group_measurements_by_date_method_term(
        _expand_multiple_measurements(measurements)
    )

    for (date, method, term_id), measurements_list in grouped_measurements.items():
        needed_depths = _get_depths_from_measurements(measurements_list)
        # For a target depth
        for depth_upper, depth_lower in needed_depths:
            modelled_value = _harmonise_measurements(
                measurements_list=measurements_list,
                standard_depth_upper=depth_upper,
                standard_depth_lower=depth_lower
            )
            if modelled_value:
                results.append(
                    _measurement(
                        value=modelled_value,
                        date=date,
                        standard_fields={
                            "depthUpper": depth_upper,
                            "depthLower": depth_lower
                        },
                        term_id=term_id
                    )
                )

    return results


def _get_depths_from_measurements(measurements: list) -> list:
    needed_depths = list(STANDARD_DEPTHS)
    for measurement in measurements:
        if (measurement.get("depthUpper"), measurement.get("depthLower")) in needed_depths:
            needed_depths.remove((int(measurement["depthUpper"]), int(measurement["depthLower"])))

    return needed_depths


def _should_run(site: dict):
    measurements = site.get("measurements", [])
    measurement_sensitivity = {
        m.get('term', {}).get('@id'): get_lookup_value(
            m.get('term', {}), LOOKUPS["measurement"], model=MODEL, model_key=MODEL_KEY
        )
        for m in measurements
    }
    # we only work with measurements with depths
    measurements_with_depths = [m for m in measurements if all([
        not measurement_sensitivity[m.get("term", {}).get('@id')],
        m.get('value', []),
        "depthUpper" in m,
        "depthLower" in m
    ])]
    has_measurements_with_depths = len(measurements_with_depths) > 0

    logRequirements(site, model=MODEL, model_key=MODEL_KEY,
                    measurements_depth_sensitive=log_as_table(measurement_sensitivity),
                    has_measurements_with_depths=has_measurements_with_depths)

    should_run = has_measurements_with_depths
    for measurement in measurements_with_depths:
        term_id = measurement.get("term", {}).get("@id", {})
        logShouldRun(site, MODEL, term_id, should_run, model_key=MODEL_KEY)
    return should_run, measurements_with_depths


def run(site: dict):
    should_run, measurements_with_depths = _should_run(site)
    return non_empty_list(flatten(_run_harmonisation(measurements=measurements_with_depths))) if should_run else []
