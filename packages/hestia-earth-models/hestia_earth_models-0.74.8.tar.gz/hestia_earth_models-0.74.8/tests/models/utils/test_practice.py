from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.models.utils.practice import _new_practice

class_path = 'hestia_earth.models.utils.practice'


@patch(f"{class_path}.include_model", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_term", return_value=TERM)
def test_new_practice(*args):
    # with a Term as string
    practice = _new_practice('term')
    assert practice == {
        '@type': 'Practice',
        'term': TERM
    }

    # with a Term as dict
    practice = _new_practice(TERM)
    assert practice == {
        '@type': 'Practice',
        'term': TERM
    }
