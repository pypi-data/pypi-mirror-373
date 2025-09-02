from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.dammgen2009.noxToAirExcreta import MODEL, TERM_ID, run, _should_run, _N2O_TERM_ID

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no practice factor => no run
    should_run, *args = _should_run({})
    assert not should_run

    # without N20 term in cycle.emissions => no run
    should_run, *args = _should_run(
        {
            "type": "Cycle",
            "emissions": [{
                "@type": "Emission",
                "term": {
                    "@id": "ch4ToAirExcreta",
                    "termType": "emission"
                },
                "value": [8.7],
            }]
        }
    )
    assert not should_run

    # with N20 term in cycle => run
    should_run, *args = _should_run(
        {
            "type": "Cycle",
            "emissions": [{
                "@type": "Emission",
                "term": {
                    "@id": _N2O_TERM_ID,
                    "termType": "emission"
                },
                "value": [10.7],
            }]
         }
    )
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
