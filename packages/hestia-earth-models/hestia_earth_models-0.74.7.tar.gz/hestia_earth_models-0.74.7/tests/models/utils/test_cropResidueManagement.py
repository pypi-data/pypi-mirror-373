from unittest.mock import patch

from hestia_earth.models.utils.cropResidueManagement import has_residue_incorporated_practice

class_path = 'hestia_earth.models.utils.cropResidueManagement'
TERMS = [
    'residueIncorporated',
    'residueIncorporatedLessThan30DaysBeforeCultivation',
    'residueIncorporatedMoreThan30DaysBeforeCultivation',
    'residueRemoved',
    'residueBurnt'
]


@patch(f"{class_path}.get_crop_residue_management_terms", return_value=TERMS)
def test_has_residue_incorporated_practice(*args):
    cycle = {'practices': [{'term': {'@id': 'residueBurnt'}}]}
    assert not has_residue_incorporated_practice(cycle)

    cycle = {'practices': [{'term': {'@id': 'residueIncorporated'}}]}
    assert has_residue_incorporated_practice(cycle) is True

    cycle = {'practices': [{'term': {'@id': 'residueIncorporatedMoreThan30DaysBeforeCultivation'}}]}
    assert has_residue_incorporated_practice(cycle) is True
