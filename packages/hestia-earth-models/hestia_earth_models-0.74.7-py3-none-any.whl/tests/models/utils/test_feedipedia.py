from unittest.mock import patch
from tests.utils import fake_new_property
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.utils.feedipedia import rescale_properties_from_dryMatter

class_path = 'hestia_earth.models.utils.feedipedia'


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_rescale_properties_from_dryMatter(*args):
    dm_prop = {
        '@type': 'Property',
        'term': {'@type': 'Term', '@id': 'dryMatter'},
        'value': 80
    }
    inputs = [
        {
            '@type': 'Input',
            'term': {'@type': 'Term', '@id': 'wheatGrain', 'termType': 'crop'},
            'properties': [dm_prop]
        }
    ]
    results = rescale_properties_from_dryMatter('model', {}, inputs)
    property = find_term_match(results[0].get('properties'), 'energyContentHigherHeatingValue')
    assert property.get('value') == 14.56
