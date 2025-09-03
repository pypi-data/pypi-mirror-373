from unittest.mock import patch
import json

from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.faostat2018.liveweightPerHead import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run_animalProduct(*args):
    with open(f"{fixtures_folder}/animalProduct/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/animalProduct/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
@patch(f"{class_path}.download_term")
def test_run_liveAnimal_chicken(mock_download_term, *args):
    with open(f"{fixtures_folder}/liveAnimal/chicken/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/liveAnimal/chicken/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    mock_download_term.return_value = {
        "@id": "meatChickenReadyToCookWeight",
        "@type": "Term",
        "units": "kg ready-to-cook weight",
        "defaultProperties": [
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, liveweight to cold carcass weight",
                    "termType": "property",
                    "@id": "processingConversionLiveweightToColdCarcassWeight",
                    "units": "%"
                },
                "value": 72.30401869158878,
                "@type": "Property"
            },
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, cold carcass weight to ready-to-cook weight",
                    "termType": "property",
                    "@id": "processingConversionColdCarcassWeightToReadyToCookWeight",
                    "units": "%"
                },
                "value": 72.45065789473684,
                "@type": "Property"
            }
        ]
    }
    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
@patch(f"{class_path}.download_term")
def test_run_liveAnimal_pig(mock_download_term, *args):
    with open(f"{fixtures_folder}/liveAnimal/pig/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/liveAnimal/pig/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    mock_download_term.return_value = {
        "@id": "meatPigColdDressedCarcassWeight",
        "@type": "Term",
        "units": "kg cold dressed carcass weight",
        "defaultProperties": [
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, liveweight to cold carcass weight",
                    "termType": "property",
                    "@id": "processingConversionLiveweightToColdCarcassWeight",
                    "units": "%"
                },
                "value": 75.22666597366735,
                "@type": "Property"
            }
        ]
    }
    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
@patch(f"{class_path}.download_term")
def test_run_liveAnimal_sheepLamb(mock_download_term, *args):
    with open(f"{fixtures_folder}/liveAnimal/sheepLamb/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/liveAnimal/sheepLamb/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    mock_download_term.return_value = {
        "@id": "meatSheepColdDressedCarcassWeight",
        "@type": "Term",
        "units": "kg cold dressed carcass weight",
        "defaultProperties": [
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, liveweight to cold carcass weight",
                    "termType": "property",
                    "@id": "processingConversionLiveweightToColdCarcassWeight",
                    "units": "%"
                },
                "value": 47.301833667687326,
                "@type": "Property"
            }
        ]
    }
    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run_liveAninal_missing_term_id(*args):
    with open(f"{fixtures_folder}/liveAnimal/missing-fao-term-id/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []
