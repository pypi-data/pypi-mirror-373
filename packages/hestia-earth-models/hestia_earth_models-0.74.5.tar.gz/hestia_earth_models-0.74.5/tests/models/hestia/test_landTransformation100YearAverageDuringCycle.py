import json
from unittest.mock import patch, Mock
import pytest

from tests.utils import fixtures_path, fake_new_indicator
from hestia_earth.models.hestia import MODEL
from hestia_earth.models.hestia.landTransformation100YearAverageDuringCycle import TERM_ID, run


class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@pytest.mark.parametrize(
    "subfolder",
    [
        "maize_brazil"
    ]
)
@patch("hestia_earth.models.hestia.resourceUse_utils._new_indicator", side_effect=fake_new_indicator)
def test_run(mock_new_indicator: Mock, subfolder):
    folder = f"{fixtures_folder}/{subfolder}"
    with open(f"{folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact_assessment = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(impact_assessment=impact_assessment)
    assert result == expected
