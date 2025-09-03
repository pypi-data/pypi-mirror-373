import os
import json
from datetime import datetime
from hestia_earth.utils.storage._s3_client import _load_from_bucket
from hestia_earth.utils.api import _safe_get_request

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_FOLDER = 'HESTIA_AGGREGATED_DATA_FOLDER'
_DATA_FOLDER = os.getenv(_ENV_FOLDER) or _CURRENT_DIR
_FILENAME = 'hestiaAggregatedData.json'
_CACHED_DATA = {}
DEFAULT_COUNTRY_ID = 'region-world'


def _today(): return datetime.now().strftime('%Y-%m-%d')


def _download_data():
    try:
        return json.loads(_load_from_bucket('hestia-data', os.path.join('data', _FILENAME)))
    except Exception:
        return _safe_get_request(f"https://hestia.earth/data/{_FILENAME}")


def _load_data():
    data = None
    filepath = os.path.join(_DATA_FOLDER, _FILENAME)

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)

    is_data_valid = data and data['date'] == _today()

    if not is_data_valid:
        data = _download_data()
        with open(filepath, 'w') as f:
            f.write(json.dumps(data))

    return data


def _get_data():
    global _CACHED_DATA  # noqa: F824
    if not _CACHED_DATA or _CACHED_DATA['date'] != _today():
        _CACHED_DATA = _load_data()
    return _CACHED_DATA


def _get_closest_id(data: dict, year: int):
    available_years = [int(y) for y in data.keys() if int(y) <= year]
    return data[str(sorted(available_years, reverse=True)[0])] if available_years else None


def find_closest_impact_id(product_id: str, country_id: str, year: int):
    """
    Find the `@id` of the closest ImpactAssessment to the target year.

    Parameters
    ----------
    product_id : str
        The `@id` of the product (Term).
    country_id : str
        The `@id` of the country (Term).
    year : int
        The target year.

    Returns
    -------
    str
        The `@id` as a string if found.
    """
    data = _get_data()
    values = data.get(product_id, {}).get(country_id, {})
    return _get_closest_id(data=values, year=year)
