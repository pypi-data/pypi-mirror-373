from unittest.mock import patch

from hestia_earth.models.utils.cropResidue import get_crop_residue_burnt_value

class_path = 'hestia_earth.models.utils.cropResidue'


@patch(f"{class_path}.find_term_match", return_value=None)
@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_get_crop_residue_burnt_value(mock_data_complete, mock_find_product):
    # product not found no data complete
    mock_data_complete.return_value = False
    mock_find_product.return_value = {}
    value = get_crop_residue_burnt_value({})
    assert value is None

    # product not found and data complete
    mock_data_complete.return_value = True
    mock_find_product.return_value = {}
    value = get_crop_residue_burnt_value({})
    assert value == 0

    # product found
    mock_find_product.return_value = {'value': [100]}
    value = get_crop_residue_burnt_value({})
    assert value == 200
