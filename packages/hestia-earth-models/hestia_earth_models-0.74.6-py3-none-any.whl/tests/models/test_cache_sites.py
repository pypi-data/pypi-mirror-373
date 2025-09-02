import os
from unittest.mock import patch, call
import json
from tests.utils import fixtures_path

from hestia_earth.models.cache_sites import run

class_path = 'hestia_earth.models.cache_sites'
fixtures_folder = os.path.join(fixtures_path, 'cache_sites')
coordinates = [{"latitude": 46.47, "longitude": 2.94}]


@patch(f"{class_path}._run_query")
def test_run(mock_run_query, *args):
    with open(f"{fixtures_folder}/data.json", encoding='utf-8') as f:
        data = json.load(f)
    with open(f"{fixtures_folder}/cache.json", encoding='utf-8') as f:
        cache = json.load(f)

    with open(f"{fixtures_folder}/rasters-no-years.json", encoding='utf-8') as f:
        rasters_no_years = json.load(f)
    with open(f"{fixtures_folder}/rasters-years.json", encoding='utf-8') as f:
        rasters_years = json.load(f)
    with open(f"{fixtures_folder}/vectors.json", encoding='utf-8') as f:
        vectors = json.load(f)

    mock_run_query.side_effect = [
        [10] * len(rasters_no_years),
        [10] * len(vectors),
        [10] * len(rasters_years)
    ]

    sites = run(sites=data.get('nodes', []), years=[2019, 2020])

    mock_run_query.assert_has_calls([
        call({
            "ee_type": "raster",
            "collections": rasters_no_years,
            "coordinates": coordinates
        }),
        call({
            "ee_type": "vector",
            "collections": vectors,
            "coordinates": coordinates
        }),
        call({
            "ee_type": "raster",
            "collections": rasters_years,
            "coordinates": coordinates
        })
    ])

    expected = [site | {'_cache': cache} for site in data.get('nodes', [])]
    assert sites == expected


@patch(f"{class_path}._run_query")
def test_run_include_region(mock_run_query, *args):
    with open(f"{fixtures_folder}/data.json", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/rasters-no-years.json", encoding='utf-8') as f:
        rasters_no_years = json.load(f)
    with open(f"{fixtures_folder}/rasters-years.json", encoding='utf-8') as f:
        rasters_years = json.load(f)
    with open(f"{fixtures_folder}/vectors-with-regions.json", encoding='utf-8') as f:
        vectors_with_regions = json.load(f)

    mock_run_query.side_effect = [
        [10] * len(rasters_no_years),
        [10] * len(vectors_with_regions),
        [10] * len(rasters_years)
    ]

    run(sites=data.get('nodes', []), years=[2019, 2020])

    mock_run_query.assert_has_calls([
        call({
            "ee_type": "raster",
            "collections": rasters_no_years,
            "coordinates": coordinates
        }),
        call({
            "ee_type": "vector",
            "collections": vectors_with_regions,
            "coordinates": coordinates
        }),
        call({
            "ee_type": "raster",
            "collections": rasters_years,
            "coordinates": coordinates
        })
    ])
