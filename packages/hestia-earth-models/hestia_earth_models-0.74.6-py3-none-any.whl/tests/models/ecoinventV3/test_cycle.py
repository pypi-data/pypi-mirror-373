import os
import json
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_emission
from hestia_earth.models.ecoinventV3.cycle import MODEL, run

class_path = f"hestia_earth.models.{MODEL}.cycle"
fixtures_folder = os.path.join(fixtures_path, MODEL, 'cycle')

TERMS_BY_ID = {
    '24EpibrassinolideTgai': {
        "defaultProperties": [{
            "@type": "Property",
            "term": {
                "@id": "activeIngredient",
                "@type": "Term"
            },
            "value": 20,
            "key": {
                "@id": "CAS-78821-43-9",
                "@type": "Term",
                "termType": "pesticideAI"
            }
        }, {
            "@type": "Property",
            "term": {
                "@id": "activeIngredient",
                "@type": "Term"
            },
            "value": 30,
            "key": {
                "@id": "CAS-78821-42-8",
                "@type": "Term",
                "termType": "pesticideAI"
            }
        }]
    }
}


def fake_download_term(term, *args):
    term_id = term.get('@id') if isinstance(term, dict) else term
    return TERMS_BY_ID.get(term_id, {})


@patch('hestia_earth.models.utils.blank_node.download_term', side_effect=fake_download_term)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_ember(*args):
    with open(f"{fixtures_folder}/ember-comparison/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/ember-comparison/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
