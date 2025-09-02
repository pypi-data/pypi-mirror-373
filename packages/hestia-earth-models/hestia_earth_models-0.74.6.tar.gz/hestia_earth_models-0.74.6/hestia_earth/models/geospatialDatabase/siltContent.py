from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import non_empty_list, flatten

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value, group_measurements_by_depth
from hestia_earth.models.utils.source import get_source
from . import MODEL, clayContent, sandContent

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {
                "@type": "Measurement",
                "term.@id": "clayContent",
                "value": ">= 0",
                "depthUpper": ">= 0",
                "depthLower": ">= 0"
            },
            {
                "@type": "Measurement",
                "term.@id": "sandContent",
                "value": ">= 0",
                "depthUpper": ">= 0",
                "depthLower": ">= 0"
            }
        ],
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "",
        "depthLower": "",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'siltContent'
OTHER_TERM_IDS = [
    clayContent.TERM_ID,
    sandContent.TERM_ID
]
BIBLIO_TITLE = 'Harmonized World Soil Database Version 2.0.'


def _measurement(site: dict, value: int, depthUpper: int, depthLower: int):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [value]
    measurement['depthUpper'] = depthUpper
    measurement['depthLower'] = depthLower
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _run(site: dict, measurements: list):
    value = 100 - sum([measurement_value(m) for m in measurements])
    return [_measurement(site, value, measurements[0].get('depthUpper'), measurements[0].get('depthLower'))]


def _should_run(site: dict):
    grouped_measurements = group_measurements_by_depth(site.get('measurements', []), include_dates=False)
    relevant_measurements = [
        [
            m for m in measurements if all([
                m.get('term', {}).get('@id') in OTHER_TERM_IDS,
                len(m.get('value', [])) > 0,
                m.get('depthUpper', -1) >= 0,
                m.get('depthLower', -1) >= 0
            ])
        ]
        for measurements in grouped_measurements.values()
    ]
    valid_measurements = [
        values for values in relevant_measurements if len(values) == len(OTHER_TERM_IDS)
    ]

    has_valid_measurements = len(valid_measurements) > 0

    logRequirements(site, model=MODEL, term=TERM_ID,
                    has_valid_measurements=has_valid_measurements,
                    measurements=log_as_table([
                        {
                            'depths': '-'.join(non_empty_list([
                                str(values[0].get('depthUpper', '')),
                                str(values[0].get('depthLower', ''))
                            ]))
                        } | {
                            term_id: measurement_value(find_term_match(values, term_id))
                            for term_id in OTHER_TERM_IDS
                        } for values in valid_measurements
                    ]))

    should_run = all([has_valid_measurements])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, valid_measurements


def run(site: dict):
    should_run, measurements = _should_run(site)
    return flatten([_run(site, values) for values in measurements]) if should_run else []
