from unittest.mock import patch
import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.completeness.cropResidue import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.completeness.{MODEL_KEY}"


@patch(f"{class_path}.get_crop_residue_terms")
def test_run(mock_terms):
    with open(f"{fixtures_path}/cycle/completeness/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    mock_terms.return_value = ['aboveGroundCropResidueRemoved']
    assert run(cycle) is True

    mock_terms.return_value = ['unknown-term']
    assert not run(cycle)
