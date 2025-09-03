from unittest.mock import patch
import json

from tests.utils import fixtures_path, _set_methodModel
from hestia_earth.models.haversineFormula.transport.distance import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.transport.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/transport/{MODEL_KEY}"


def fake_download_term(id: str, *args):
    return {
        'GADM-FRA': {'latitude': 46.55891593, 'longitude': 2.55355253},
        'GADM-CHN': {'latitude': 36.56069891, 'longitude': 103.8579343}
    }[id]


@patch(f"{class_path}.download_term", side_effect=fake_download_term)
@patch(f"{class_path}.include_methodModel", side_effect=_set_methodModel)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
