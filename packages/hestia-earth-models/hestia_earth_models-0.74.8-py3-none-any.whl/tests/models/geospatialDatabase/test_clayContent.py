from unittest.mock import patch, call
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.geospatialDatabase.clayContent import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.should_download", return_value=True)
@patch(f"{class_path}.has_geospatial_data")
def test_should_run(mock_has_geospatial_data, *args):
    site = {}

    mock_has_geospatial_data.return_value = False
    assert not _should_run(site)

    mock_has_geospatial_data.return_value = True
    assert _should_run(site) is True

    # with other texture measurements => not run
    site['measurements'] = [{'term': {'@id': 'clayContent'}}]
    assert not _should_run(site)


@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.download", return_value=None)
def test_run(mock_download, *args):
    with open(f"{fixtures_path}/{MODEL}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    run(site)
    base_params = {'ee_type': 'raster', 'reducer': 'mean'}
    mock_download.assert_has_calls([
        call(TERM_ID, site, base_params | {
            'collection': 'T_CLAY_v2_depth_1', 'depthUpper': 0, 'depthLower': 20
        }),
        call(TERM_ID, site, base_params | {
            'collection': 'T_CLAY_v2_depth_2', 'depthUpper': 20, 'depthLower': 40
        }),
        call(TERM_ID, site, base_params | {
            'collection': 'T_CLAY_v2_depth_3', 'depthUpper': 40, 'depthLower': 60
        }),
        call(TERM_ID, site, base_params | {
            'collection': 'T_CLAY_v2_depth_4', 'depthUpper': 60, 'depthLower': 80
        })
    ])
