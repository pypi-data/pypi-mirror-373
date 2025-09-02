from typing import Union, List
from functools import reduce
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils import CACHE_KEY, cached_value, first_day_of_month, last_day_of_month
from hestia_earth.models.utils.site import CACHE_YEARS_KEY
from hestia_earth.models.geospatialDatabase.utils import (
    MAX_AREA_SIZE, CACHE_VALUE, CACHE_AREA_SIZE,
    has_geospatial_data, has_coordinates, get_area_size, geospatial_data, _run_query, _collection_name, _cache_sub_key
)
from hestia_earth.models.geospatialDatabase import list_ee_params

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ]
    }
}
RETURNS = {
    "Site": {}
}


def cache_site_results(results: list, collections: list, area_size: int = None):
    def _combine_result(group: dict, index: int):
        collection = collections[index]
        name = collection.get('name')
        value = results[index]
        cache_sub_key = _cache_sub_key(collection)
        data = (group.get(name, {}) | {cache_sub_key: value} if cache_sub_key else value)
        return group | {name: data}

    return reduce(_combine_result, range(0, len(results)), {}) | (
        {CACHE_AREA_SIZE: area_size} if area_size is not None else {}
    )


def _is_collection_by_year(collection: dict):
    return any([
        'year' in collection,
        'start_date' in collection,
        'end_date' in collection
    ])


def _extend_collection_by_month(year: int):
    return [{
        'start_date': first_day_of_month(year, month).strftime('%Y-%m-%d'),
        'end_date': last_day_of_month(year, month).strftime('%Y-%m-%d')
    } for month in range(1, 13)]


def _extend_collection_data(name: str, collection: dict):
    return collection | {'name': name, 'collection': _collection_name(collection.get('collection'))}


def _extend_collection(name: str, collection: Union[List[dict], dict], years: list = []):
    year_params = [{'year': str(year)} for year in years]
    # fetch from first year to last
    month_years = range(years[0], years[-1] + 1) if len(years) > 1 else years
    month_params = flatten(map(_extend_collection_by_month, month_years))

    return [
        (_extend_collection_data(name, collection) | params) for params in year_params
    ] if name.endswith('Annual') else [
        (_extend_collection_data(name, collection) | params) for params in month_params
    ] if name.endswith('Monthly') else [
        _extend_collection_data(name, col) for col in collection
    ] if isinstance(collection, list) else [
        _extend_collection_data(name, collection)
    ]


def _extend_collections(values: list, years: list = []):
    return flatten([
        _extend_collection(value.get('name'), value.get('params'), years) for value in values
    ])


def _is_type(value: dict, ee_type: str):
    params = value.get('params')
    return any([
        p.get('ee_type') == ee_type for p in params
    ]) if isinstance(params, list) else params.get('ee_type') == ee_type


def list_rasters(years: list = [], years_only: bool = False):
    ee_params = list_ee_params()
    # only cache `raster` results as can be combined in a single query
    rasters = [value for value in ee_params if _is_type(value, 'raster')]
    rasters = _extend_collections(rasters, years or [])
    rasters = [raster for raster in rasters if not years_only or _is_collection_by_year(raster)]

    return rasters


def list_vectors(sites: list):
    ee_params = list_ee_params()

    vectors = [value for value in ee_params if _is_type(value, 'vector')]
    vectors = [
        value for value in vectors
        # name of the model is the key in the data. If the key is present in all sites, we don't need to query
        if all([not s.get(value.get('name')) for s in sites])
    ]
    # no vectors are running with specific years
    vectors = _extend_collections(vectors)

    return vectors


def _cache_results(site: dict, area_size: float):
    # to fetch data related to the year
    years = cached_value(site, key=CACHE_YEARS_KEY, default=[])
    rasters = list_rasters(years)
    vectors = list_vectors([site])

    raster_results = _run_query({
        'ee_type': 'raster',
        'collections': rasters
    } | geospatial_data(site)) if rasters else []

    vector_results = _run_query({
        'ee_type': 'vector',
        'collections': vectors
    } | geospatial_data(site)) if vectors else []

    return cache_site_results(raster_results + vector_results, rasters + vectors, area_size)


def _should_run(site: dict, area_size: float = None, check_has_cache: bool = True):
    area_size = area_size or get_area_size(site)
    contains_geospatial_data = has_geospatial_data(site)
    contains_coordinates = has_coordinates(site)
    has_cache = check_has_cache and cached_value(site, CACHE_VALUE) is not None

    debugValues(site,
                area_size=area_size,
                MAX_AREA_SIZE=MAX_AREA_SIZE,
                contains_geospatial_data=contains_geospatial_data,
                has_cache=has_cache)

    should_run = all([
        not has_cache,
        contains_coordinates or (area_size is not None and area_size <= MAX_AREA_SIZE),
        contains_geospatial_data
    ])
    return should_run, area_size


def run(site: dict):
    should_run, area_size = _should_run(site)
    return {
        **site,
        CACHE_KEY: {**cached_value(site), CACHE_VALUE: _cache_results(site, area_size)}
    } if should_run else site
