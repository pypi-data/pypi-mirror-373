from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.models.utils.property import _new_property

class_path = 'hestia_earth.models.utils.property'


@patch(f'{class_path}.include_methodModel', side_effect=lambda n, x: n)
@patch(f'{class_path}.download_term', return_value=TERM)
def test_new_property(*args):
    # with a Term as string
    property = _new_property('term')
    assert property == {
        '@type': 'Property',
        'term': TERM
    }

    # with a Term as dict
    property = _new_property(TERM)
    assert property == {
        '@type': 'Property',
        'term': TERM
    }
