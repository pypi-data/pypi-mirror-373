import os
import json
from area import area
from functools import reduce, lru_cache
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import debugValues, logErrorRun, logRequirements
from hestia_earth.models.utils.site import cached_value, region_factor, region_level_1_id
from hestia_earth.models.utils.term import download_term
from . import MODEL

MAX_AREA_SIZE = int(os.getenv('MAX_AREA_SIZE', '5000'))
_ENABLE_CACHE_BOUNDARY_AREA = os.getenv('CACHE_BOUNDARY_AREA', 'false') == 'true'
CACHE_VALUE = MODEL
CACHE_AREA_SIZE = 'areaSize'
GEOPANDAS_COLLECTION_NAME = {
    'AWARE': 'aware/aware',
    'Terrestrial_Ecoregions_World': 'ecoregion/ecoregions',
    'gadm36_0': 'gadm/gadm36_0',
    'gadm36_1': 'gadm/gadm36_1',
    'gadm36_2': 'gadm/gadm36_2',
    'gadm36_3': 'gadm/gadm36_3',
    'gadm36_4': 'gadm/gadm36_4',
    'gadm36_5': 'gadm/gadm36_5'
}
KELVIN_0 = 273.15


def to_celcius(kelvin_value: int): return kelvin_value - KELVIN_0 if kelvin_value else None


def use_geopandas(): return os.getenv('HEE_USE_GEOPANDAS', 'false') == 'true'


def _has_cache(site: dict):
    cache = cached_value(site, key=CACHE_VALUE, default=None)
    return bool(cache)


def _cached_value(site: dict, key: str):
    return cached_value(site, key=CACHE_VALUE, default={}).get(key)


def _collection_name(id: str):
    name = id if '/' in id else f"users/hestiaplatform/{id}"
    return GEOPANDAS_COLLECTION_NAME.get(id, name) if use_geopandas() else name


def has_coordinates(site: dict): return all([site.get('latitude') is not None, site.get('longitude') is not None])


def has_boundary(site: dict): return site.get('boundary') is not None


def _site_gadm_id(site: dict): return site.get('region', site.get('country', {})).get('@id')


def has_geospatial_data(site: dict):
    """
    Determines whether the Site has enough geospatial data to run calculations. We are checking for:
    1. If the coordinates (latitude and longitude) are present
    2. Otherwise if the `region` or `country` is present
    3. Otherwise if the `boundary` is present
    Note: this is a general pre-check only, each model can have 1 or more other checks.

    Parameters
    ----------
    site : dict
        The `Site` node.

    Returns
    -------
    bool
        If we should run geospatial calculations on this model or not.
    """
    return has_coordinates(site) or _site_gadm_id(site) is not None or has_boundary(site)


def geospatial_data(site: dict, only_coordinates=False):
    return {
        'coordinates': [{'latitude': site.get('latitude'), 'longitude': site.get('longitude')}]
    } if has_coordinates(site) else ({} if only_coordinates else {
        'boundaries': [site.get('boundary')]
    } if has_boundary(site) else {
        'gadm-ids': [_site_gadm_id(site)]
    })


def _geojson_area_size(boundary: dict):
    return (
        _geojson_area_size(boundary.get('geometry')) if 'geometry' in boundary else
        reduce(lambda p, c: p + _geojson_area_size(c), boundary.get('features'), 0) if 'features' in boundary
        else area(boundary) / 1_000_000
    )


@lru_cache()
def _cached_boundary_area_size(boundary: str):
    try:
        return _geojson_area_size(json.loads(boundary))
    except Exception:
        return None


def _get_boundary_area_size(boundary: dict):
    return _cached_boundary_area_size(
        boundary=json.dumps(boundary)
    ) if _ENABLE_CACHE_BOUNDARY_AREA else _geojson_area_size(boundary=boundary)


def _get_region_area_size(site: dict):
    term = site.get('region', site.get('country'))
    return term.get('area', (download_term(term.get('@id'), TermTermType.REGION) or {}).get('area')) if term else None


def get_area_size(site: dict):
    return _cached_value(site, CACHE_AREA_SIZE) or (
        None if has_coordinates(site) else (
            # fallback if `boundary` provided but no `boundaryArea` was computed
            site.get('boundaryArea') or _get_boundary_area_size(site.get('boundary'))
        ) if has_boundary(site) else _get_region_area_size(site)
    )


def _is_below_max_size(term: str, site: dict) -> bool:
    current_size = _cached_value(site, CACHE_AREA_SIZE) or get_area_size(site)
    if current_size is not None:
        logRequirements(site, model=MODEL, term=term,
                        current_size=round(float(current_size), 5),
                        max_area_size=MAX_AREA_SIZE)
        return current_size <= MAX_AREA_SIZE
    return True


def should_download(term: str, site: dict) -> bool:
    return has_coordinates(site) or _is_below_max_size(term, site)


def _run_query(query: dict):
    try:
        from hestia_earth.earth_engine import run
    except ImportError:
        raise ImportError("Run `pip install hestia_earth.earth_engine` to use this functionality")

    return run(query)


def _parse_run_query(term: str, query: dict):
    try:
        res = _run_query(query)
        return res[0] if len(res) > 0 else None
    except Exception as e:
        logErrorRun(MODEL, term, str(e))
        return None


def _cache_sub_key(collection: dict):
    return '-'.join(non_empty_list([
        str(collection.get('year', '')),
        str(collection.get('start_date', '')),
        str(collection.get('end_date', '')),
        str(collection.get('depthUpper', '')),
        str(collection.get('depthLower', ''))
    ]))


def _get_cached_data(term: str, site: dict, data: dict):
    cache = _cached_value(site, term)
    cache_sub_key = _cache_sub_key(data)
    # data can be grouped by year when required
    value = cache.get(cache_sub_key) if all([
        isinstance(cache, dict),
        cache_sub_key
    ]) else cache
    debugValues(site, model=MODEL, term=term, value_from_cache=value)
    return value


def download(term: str, site: dict, data: dict, only_coordinates=False) -> dict:
    """
    Downloads data from HESTIA Earth Engine API.

    Returns
    -------
    dict
        Data returned from the API.
    """
    # check if we have cached the result already, else run and parse result
    if _has_cache(site):
        # even if the cached value is null, we do not want to run the query again
        # TODO: we might want to store the date it was cached, and run again if more than 30 days
        return _get_cached_data(term, site, data)

    location_data = geospatial_data(site, only_coordinates=only_coordinates)
    query = {
        'ee_type': data.get('ee_type'),
        **location_data,
        'collections': [
            {
                **data,
                'collection': _collection_name(data.get('collection'))
            }
        ]
    }
    value = _parse_run_query(term, query)
    if value is None:
        debugValues(site, model=MODEL, term=term, value_from_earth_engine=None)
    return value


def get_region_factor(term_id: str, site: dict, termType: TermTermType = TermTermType.MEASUREMENT):
    region_id = region_level_1_id(site.get('region', {}).get('@id'))
    country_id = site.get('country', {}).get('@id')
    return (
        # `region-measurement` only exists for countries
        region_factor(MODEL, region_id, term_id, termType) if termType != TermTermType.MEASUREMENT else None
    ) or region_factor(MODEL, country_id, term_id, termType)
