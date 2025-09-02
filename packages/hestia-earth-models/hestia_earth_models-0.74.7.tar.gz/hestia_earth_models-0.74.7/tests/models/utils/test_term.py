from unittest.mock import patch

from hestia_earth.models.utils.term import (
    get_liquid_fuel_terms, get_irrigation_terms, get_urea_terms, get_excreta_N_terms, get_excreta_VS_terms,
    get_generic_crop, get_rice_paddy_terms, get_tillage_terms, get_crop_residue_terms, get_cover_crop_property_terms,
    get_crop_residue_incorporated_or_left_on_field_terms, get_irrigated_terms, get_residue_removed_or_burnt_terms,
    get_upland_rice_land_cover_terms, get_upland_rice_crop_terms
)

class_path = 'hestia_earth.models.utils.term'


@patch(f"{class_path}.search")
def test_get_liquid_fuel_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_liquid_fuel_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_irrigation_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_irrigation_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_urea_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_urea_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_excreta_N_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_excreta_N_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_excreta_VS_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_excreta_VS_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_generic_crop(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_generic_crop() == {'@id': id}


@patch(f"{class_path}.search")
def test_get_rice_paddy_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_rice_paddy_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_tillage_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_tillage_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_crop_residue_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_crop_residue_terms() == [id]


@patch(f"{class_path}.search")
def test_get_cover_crop_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_cover_crop_property_terms() == [id]


@patch(f"{class_path}.search")
def test_get_crop_residue_incorporated_or_left_on_field_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_crop_residue_incorporated_or_left_on_field_terms() == [id]


@patch(f"{class_path}.search")
def test_get_irrigated_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_irrigated_terms() == [id]


@patch(f"{class_path}.search")
def test_get_residue_removed_or_burnt_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_residue_removed_or_burnt_terms() == [id]


@patch(f"{class_path}.search")
def test_get_upland_rice_land_cover_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_upland_rice_land_cover_terms() == [id]


@patch(f"{class_path}.search")
def test_get_upland_rice_crop_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_upland_rice_crop_terms() == [id]
