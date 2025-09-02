import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.impact_assessment.allocationMethod import MODEL_KEY, run, _should_run

fixtures_folder = f"{fixtures_path}/impact_assessment/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,impact,expected_should_run',
    [
        (
            'no updated/modified => no run',
            {},
            False
        ),
        (
            'updated organic => no run',
            {'updated': ['organic']},
            False
        ),
        (
            'updated impacts => run',
            {'updated': ['impacts']},
            True
        ),
        (
            'added emissions => run',
            {'updated': ['emissionsResourceUse']},
            True
        )
    ]
)
def test_should_run(test_name, impact, expected_should_run):
    should_run = _should_run(impact)
    assert should_run == expected_should_run, test_name


def test_run():
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    result = run(impact)
    assert result == expected
