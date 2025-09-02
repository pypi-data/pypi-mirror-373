from unittest.mock import patch
import json

from tests.utils import fixtures_path, TERM
from hestia_earth.models.utils.product import (
    _new_product, find_by_product, abg_residue_on_field_nitrogen_content
)

class_path = 'hestia_earth.models.utils.product'
fixtures_folder = f"{fixtures_path}/utils/product"


@patch(f"{class_path}.include_model", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_term", return_value=TERM)
def test_new_product(*args):
    # with a Term as string
    product = _new_product('term', 10)
    assert product == {
        '@type': 'Product',
        'term': TERM,
        'value': [10]
    }

    # with a Term as dict
    product = _new_product(TERM, 10)
    assert product == {
        '@type': 'Product',
        'term': TERM,
        'value': [10]
    }

    # no value
    product = _new_product(TERM)
    assert product == {
        '@type': 'Product',
        'term': TERM
    }


def test_find_by_product():
    product = {'term': {'@id': 'term 1'}, 'variety': 'var 1'}
    cycle = {
        'products': [
            product,
            {'term': {'@id': 'term 1'}, 'variety': 'var 2'},
            {'term': {'@id': 'term 2'}, 'variety': 'var 1'}
        ]
    }
    assert find_by_product(cycle, product) == product

    with open(f"{fixtures_folder}/find-by-product.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)
    transformations = cycle.get('transformations')

    product = transformations[0].get('inputs')[0]
    assert find_by_product(cycle, product).get('term', {}).get('@id') == product.get('term', {}).get('@id')

    product = transformations[0].get('products')[0]
    assert find_by_product(cycle, product).get('term', {}).get('@id') == product.get('term', {}).get('@id')

    product = transformations[1].get('inputs')[0]
    assert find_by_product(transformations[0], product).get('term', {}).get('@id') == product.get('term', {}).get('@id')


def test_abg_residue_on_field_nitrogen_content_no_products():
    assert abg_residue_on_field_nitrogen_content([]) == 0


def test_abg_residue_on_field_nitrogen_content():
    with open(f"{fixtures_folder}/products-cropResidue.jsonld", encoding='utf-8') as f:
        products = json.load(f)

    assert abg_residue_on_field_nitrogen_content(products) == 0.8445757894736851
