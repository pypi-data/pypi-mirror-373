from unittest.mock import Mock, patch
from hestia_earth.schema import TermTermType

from hestia_earth.models.site.pre_checks.country import run

class_path = 'hestia_earth.models.site.pre_checks.country'


@patch(f"{class_path}.download_term")
def test_run(mock_download_term: Mock):
    site = {'country': {'@type': 'Term', '@id': 'GADM-GBR'}}
    run(site)
    mock_download_term.assert_called_once_with('GADM-GBR', TermTermType.REGION)
