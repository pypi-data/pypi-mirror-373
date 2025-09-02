from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path, fake_new_practice
from hestia_earth.models.hestia.pastureSystem import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"

PASTURE_TERMS = ['hillyPastureSystem', 'confinedPastureSystem']


@patch(f"{class_path}.get_pasture_system_terms", return_value=PASTURE_TERMS)
@patch(f"{class_path}.valid_site_type", return_value=False)
@patch(f"{class_path}.find_primary_product", return_value=None)
def test_should_run(mock_primary_product, mock_valid_site_type, *args):
    cycle = {}

    # no primary product => no run
    mock_primary_product.return_value = {}
    assert not _should_run(cycle)

    # with primary product => not run
    product = {
        'term': {'termType': TermTermType.LIVEANIMAL.value},
        'value': [2]
    }
    mock_primary_product.return_value = product
    assert not _should_run(cycle)

    # with valid siteType => run
    mock_valid_site_type.return_value = True
    assert _should_run(cycle) is True


@patch(f"{class_path}.get_pasture_system_terms", return_value=PASTURE_TERMS)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*argsm):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
