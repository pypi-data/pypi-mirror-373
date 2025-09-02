from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_download_term

from hestia_earth.models.geospatialDatabase.region import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"{class_path}.has_coordinates")
def test_should_run(mock_has_coordinates, *args):
    mock_has_coordinates.return_value = True
    assert _should_run({}) is True

    mock_has_coordinates.return_value = False
    assert not _should_run({})


@patch(f"{class_path}.download_term", side_effect=fake_download_term)
@patch(f"{class_path}.download", return_value=None)
def test_run(mock_download, *args):
    with open(f"{fixtures_path}/{MODEL}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    run(site)
    mock_download.assert_called_once()
