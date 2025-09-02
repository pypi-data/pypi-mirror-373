from unittest.mock import patch

from hestia_earth.models.schmidt2007.utils import get_waste_values

class_path = 'hestia_earth.models.schmidt2007.utils'
TERMS = [
    'Oil palm mill effluent (waste)'
]


@patch(f"{class_path}._is_term_type_complete", return_value=True)
def test_get_waste_values_no_inputs_complete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_waste_values('ch4ToAirWasteTreatment', cycle, '') == [0]

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_waste_values('ch4ToAirWasteTreatment', cycle, '') == []


@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_get_waste_values_no_inputs_incomplete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_waste_values('ch4ToAirWasteTreatment', cycle, '') == []

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_waste_values('ch4ToAirWasteTreatment', cycle, '') == []


def test_get_waste_values(*args):
    cycle = {
        '@type': 'Cycle',
        'products': [
            {
                'term': {'@id': 'oilPalmMillEffluentWaste', 'termType': 'waste'},
                'value': [100]
            }
        ]
    }
    assert get_waste_values('ch4ToAirWasteTreatment', cycle, 'ch4EfSchmidt2007') == [1.3]
