import pytest
from unittest.mock import patch
from hestia_earth.schema import TermTermType
from tests.utils import TERM

from hestia_earth.models.utils.input import _new_input, get_feed_inputs

class_path = 'hestia_earth.models.utils.input'


@patch(f"{class_path}.include_model", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_term", return_value=TERM)
def test_new_input(*args):
    # with a Term as string
    input = _new_input('term')
    assert input == {
        '@type': 'Input',
        'term': TERM
    }

    # with a Term as dict
    input = _new_input(TERM)
    assert input == {
        '@type': 'Input',
        'term': TERM
    }


@pytest.mark.parametrize(
    'test_name,cycle,expected_input_length',
    [
        (
            'no inputs',
            {},
            0
        ),
        (
            'with crop feed',
            {
                'inputs': [{
                    'term': {'units': 'kg', 'termType': TermTermType.CROP.value, '@id': 'wheatGrain'},
                    'isAnimalFeed': True,
                    'value': [10]
                }]
            },
            1
        ),
        (
            'with crop no feed',
            {
                'inputs': [{
                    'term': {'units': 'kg', 'termType': TermTermType.CROP.value, '@id': 'wheatGrain'},
                    'isAnimalFeed': False,
                    'value': [10]
                }]
            },
            0
        ),
        (
            'with feed food additive and energy content',
            {
                'inputs': [{
                    'term': {
                        'units': 'kg', 'termType': TermTermType.FEEDFOODADDITIVE.value, '@id': 'aminoAcidsUnspecified'
                    },
                    'isAnimalFeed': True,
                    'value': [10]
                }]
            },
            1
        ),
        (
            'with feed food additive not energy content',
            {
                'inputs': [{
                    'term': {
                        'units': 'kg', 'termType': TermTermType.FEEDFOODADDITIVE.value, '@id': 'premixUnspecified'
                    },
                    'isAnimalFeed': True,
                    'value': [10]
                }]
            },
            0
        ),
    ]
)
def test_get_feed_inputs(test_name, cycle, expected_input_length):
    assert len(get_feed_inputs(cycle)) == expected_input_length, test_name
