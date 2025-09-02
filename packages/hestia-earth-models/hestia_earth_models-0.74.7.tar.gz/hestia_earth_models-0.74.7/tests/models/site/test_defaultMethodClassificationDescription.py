import json
from tests.utils import fixtures_path

from hestia_earth.models.site.defaultMethodClassificationDescription import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


def test_run():
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    result = run(site)
    assert result == expected


def test_run_no_value():
    site = {'management': [{'@type': 'Management'}]}
    result = run(site)
    assert result == 'Data calculated by merging real land use histories and modelled land use histories for each Site.'
