import os
import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.pooreNemecek2018.utils import MODEL, get_excreta_product_with_ratio

fixtures_folder = os.path.join(fixtures_path, MODEL, 'utils')


@pytest.mark.parametrize(
    'folder',
    [
        ('no-system'),
        ('single-system'),
        ('multiple-systems'),
    ]
)
def test_get_excreta_product_with_ratio(folder: str):
    with open(os.path.join(fixtures_folder, folder, 'cycle.jsonld'), 'r') as f:
        cycle = json.load(f)

    with open(os.path.join(fixtures_folder, folder, 'result.jsonld'), 'r') as f:
        expected = json.load(f)

    assert get_excreta_product_with_ratio(cycle, lookup='excretaKgNTermIds') == expected, folder
