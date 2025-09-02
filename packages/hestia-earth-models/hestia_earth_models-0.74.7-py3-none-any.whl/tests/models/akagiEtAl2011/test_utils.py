from unittest.mock import patch

from hestia_earth.models.akagiEtAl2011.utils import MODEL, _should_run

class_path = f"hestia_earth.models.{MODEL}.utils"


@patch(f"{class_path}.get_lookup_value", return_value=10)
@patch(f"{class_path}.get_crop_residue_burnt_value")
def test_should_run(mock_product_value, *args):
    # no products => no run
    mock_product_value.return_value = None
    should_run, *args = _should_run('', {})
    assert not should_run

    # with products => run
    mock_product_value.return_value = 10
    should_run, *args = _should_run('', {})
    assert should_run is True
