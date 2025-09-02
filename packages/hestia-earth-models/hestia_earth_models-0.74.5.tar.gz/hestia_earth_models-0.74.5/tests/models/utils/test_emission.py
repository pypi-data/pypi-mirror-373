from pytest import mark
from unittest.mock import patch

from hestia_earth.schema import EmissionMethodTier

from tests.utils import TERM
from hestia_earth.models.utils.emission import _new_emission, min_emission_method_tier

class_path = 'hestia_earth.models.utils.emission'


@patch(f'{class_path}.include_methodModel', side_effect=lambda n, x: n)
@patch(f'{class_path}.download_term', return_value=TERM)
def test_new_emission(*args):
    # with a Term as string
    emission = _new_emission('term')
    assert emission == {
        '@type': 'Emission',
        'term': TERM
    }

    # with a Term as dict
    emission = _new_emission(TERM)
    assert emission == {
        '@type': 'Emission',
        'term': TERM
    }


@mark.parametrize(
    "input, expected",
    [
        (
            (
                EmissionMethodTier.TIER_1,
                EmissionMethodTier.TIER_2,
                EmissionMethodTier.TIER_3
            ),
            EmissionMethodTier.TIER_1
        ),
        (
            [
                EmissionMethodTier.TIER_1,
                EmissionMethodTier.TIER_2,
                EmissionMethodTier.TIER_3
            ],
            EmissionMethodTier.TIER_1
        ),
        (
            [], EmissionMethodTier.NOT_RELEVANT
        ),
        (
            (
                EmissionMethodTier.TIER_1.value,
                EmissionMethodTier.TIER_2.value,
                EmissionMethodTier.TIER_3.value
            ),
            EmissionMethodTier.TIER_1
        ),
        (
            [
                EmissionMethodTier.TIER_1.value,
                EmissionMethodTier.TIER_2.value,
                EmissionMethodTier.TIER_3.value
            ],
            EmissionMethodTier.TIER_1
        ),

    ],
    ids=["Enum", "list[Enum]", "None", "str", "list[str]"]
)
def test_min_emission_method_tier(input, expected):
    result = min_emission_method_tier(input)
    assert result == expected
