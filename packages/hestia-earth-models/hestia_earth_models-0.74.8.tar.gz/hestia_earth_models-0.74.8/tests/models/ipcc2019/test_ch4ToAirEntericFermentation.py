from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirEntericFermentation import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

TERMS_BY_ID = {
    'energyContentHigherHeatingValue': {'units': 'MJ / kg'}
}
IONOPHORE_TERMS = ['ionophores', 'ionophoreAntibiotics']


def fake_download_term(term_id: str, *args): return TERMS_BY_ID.get(term_id, {'@id': term_id, 'units': '%'})


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch(f"{class_path}.get_default_digestibility", return_value=70)
@patch(f"{class_path}.find_primary_product", return_value={'term': {'@id': 'pig'}})
@patch(f"{class_path}._get_lookup_value", return_value=0)
@patch(f"{class_path}.get_total_value_converted_with_min_ratio", return_value=0)
def test_should_run(mock_feed, mock_lookup_value, *args):
    cycle = {
        "completeness": {"animalFeed": True, "freshForage": True},
        "inputs": [
            {
                "term": {
                    "@type": "Term",
                    "termType": "crop",
                    "@id": "sugarcaneMolasses",
                    "units": "kg",
                },
                "value": [0.000618],
            }
        ]
    }
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with fermentation factor => no run
    mock_lookup_value.return_value = 2
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with feed  => run
    mock_feed.return_value = 2
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_dairy(*args):
    with open(f"{fixtures_folder}/dairy-buffalo-cows/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/dairy-buffalo-cows/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=['milkYieldPerBuffaloRaw'])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_milkYield(*args):
    with open(f"{fixtures_folder}/with-milkYield/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-milkYield/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_non_dairy(*args):
    with open(f"{fixtures_folder}/non-dairy-buffalo-cows/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/non-dairy-buffalo-cows/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_ionophores(*args):
    with open(f"{fixtures_folder}/with-ionophores/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-ionophores/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_without_ionophores(*args):
    with open(f"{fixtures_folder}/without-ionophores/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/without-ionophores/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_no_feed(*args):
    with open(f"{fixtures_folder}/no-feed/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    result = run(cycle)
    assert result == []


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.property.get_node_property', return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_system(*args):
    with open(f"{fixtures_folder}/with-system/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-system/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_ionophore_terms", return_value=IONOPHORE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=[])
@patch("hestia_earth.models.utils.property.download_term", return_value={})
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_default(*args):
    with open(f"{fixtures_folder}/default-value/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/default-value/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
