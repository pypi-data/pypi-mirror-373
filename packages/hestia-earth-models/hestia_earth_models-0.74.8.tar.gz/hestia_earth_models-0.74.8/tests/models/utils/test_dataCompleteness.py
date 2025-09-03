from unittest.mock import Mock, patch
from hestia_earth.schema import TermTermType

from hestia_earth.models.utils.completeness import _is_term_type_complete, _is_term_type_incomplete

class_path = 'hestia_earth.models.utils.completeness'


@patch(f"{class_path}.download_term")
def test_is_term_type_complete(mock_download: Mock):
    cycle = {'completeness': {}}

    cycle['completeness'][TermTermType.CROPRESIDUE.value] = True
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert _is_term_type_complete(cycle, 'termid')

    cycle['completeness'][TermTermType.CROPRESIDUE.value] = False
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert not _is_term_type_complete(cycle, 'termid')

    # termType not in completeness
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUEMANAGEMENT.value
    }
    assert not _is_term_type_complete(cycle, 'termid')


@patch(f"{class_path}.download_term")
def test_is_term_type_incomplete(mock_download: Mock):
    cycle = {'completeness': {}}

    cycle['completeness'][TermTermType.CROPRESIDUE.value] = True
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert not _is_term_type_incomplete(cycle, 'termid')

    cycle['completeness'][TermTermType.CROPRESIDUE.value] = False
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert _is_term_type_incomplete(cycle, 'termid')

    # termType not in completeness
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUEMANAGEMENT.value
    }
    assert _is_term_type_incomplete(cycle, 'termid')
