from hestia_earth.models.log import logRequirements
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.measurement import measurement_value
from hestia_earth.models.utils.blank_node import most_relevant_blank_node_by_id
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.soilAmendment": "False",
        "endDate": "",
        "site": {
            "@type": "Site",
            "measurements": [{"@type": "Measurement", "value": "", "term.@id": "soilPh"}]
        }
    }
}
RETURNS = {
    "Completeness": {
        "soilAmendment": ""
    }
}
MODEL_KEY = 'soilAmendment'


def run(cycle: dict):
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    soilPh_measurement = most_relevant_blank_node_by_id(measurements, 'soilPh', end_date)
    soilPh = measurement_value(soilPh_measurement)

    soilPh_added = is_from_model(soilPh_measurement)
    soilPh_above_6_5 = soilPh is not None and soilPh > 6.5

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    soilPh_added=soilPh_added,
                    soilPh_above_6_5=soilPh_above_6_5)

    return all([soilPh_added, soilPh_above_6_5])
