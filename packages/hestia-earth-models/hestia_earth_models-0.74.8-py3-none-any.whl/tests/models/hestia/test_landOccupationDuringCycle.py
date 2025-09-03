import json
from os.path import isfile
from pytest import mark
from unittest.mock import patch, MagicMock

from hestia_earth.models.hestia.landOccupationDuringCycle import MODEL, TERM_ID, run, _should_run

from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def _load_fixture(file_name: str, default=None):
    path = f"{fixtures_folder}/{file_name}.jsonld"
    if isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


# subfolder, should_run
PARAMS_SHOULD_RUN = [
    ("arable", True),
    ("permanent", True),
    ("animal", True),
    ("animal-multi-country", True),
    ("arable-missing-evs", False),              # no economicValueShare on product
    ("arable-zero-evs", True),                  # economicValueShare is `0` -> run, with 0% allocated
    ("animal-missing-other-site-data", False),  # mis-matched `otherSites` and `otherSitesDuration`
    ("animal-missing-site-data", False),        # closes #1341
    ("poore-nemecek-2018-orchard", True),       # ensure model returns the same value as deprecated one
    ("poore-nemecek-2018-cereal", True)         # ensure model returns the same value as deprecated one
]
IDS_SHOULD_RUN = [p[0] for p in PARAMS_SHOULD_RUN]


@mark.parametrize("subfolder, expected", PARAMS_SHOULD_RUN, ids=IDS_SHOULD_RUN)
def test_should_run(
    subfolder: str,
    expected: bool
):
    impact = _load_fixture(f"{subfolder}/impact-assessment", {})
    cycle = _load_fixture(f"{subfolder}/cycle", {})

    impact["cycle"] = cycle

    result, *args = _should_run(impact)
    assert result == expected


PARAMS_RUN = [subfolder for subfolder, should_run in PARAMS_SHOULD_RUN if should_run]


@mark.parametrize("subfolder", PARAMS_RUN)
@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(
    _mock_new_indicator: MagicMock,
    subfolder: str
):
    impact = _load_fixture(f"{subfolder}/impact-assessment", {})
    cycle = _load_fixture(f"{subfolder}/cycle", {})
    expected = _load_fixture(f"{subfolder}/result", {})

    impact["cycle"] = cycle

    result = run(impact)
    assert result == expected
