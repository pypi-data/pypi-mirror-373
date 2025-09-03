import pytest

from hestia_earth.models.utils.impact_assessment import impact_emission_lookup_value, get_region_id, get_country_id


def test_impact_emission_lookup_value():
    impact = {
        'emissionsResourceUse': [
            {
                'term': {
                    '@id': 'ch4ToAirSoilFlux',
                    'termType': 'emission'
                },
                'value': 100
            }
        ]
    }
    # multiplies the emissionsResourceUse values with a coefficient
    assert impact_emission_lookup_value('', '', impact, 'co2EqGwp100ExcludingClimate-CarbonFeedbacksIpcc2013') == 2800


@pytest.mark.parametrize(
    'impact,expected',
    [
        ({}, None),
        ({'country': {'@id': ''}}, None),
        ({'country': {'@id': 'region-world'}}, 'region-world'),
        ({'country': {'@id': 'GADM-AUS'}}, 'GADM-AUS'),
        ({'site': {'country': {'@id': 'GADM-AUS'}, 'region': {'@id': 'GADM-AUS.101_1'}}}, 'GADM-AUS.101_1'),
        ({'site': {'region': {'@id': 'GADM-ZAF.5.1.2_1'}}}, 'GADM-ZAF.5_1'),
    ]
)
def test_get_region_id(impact: dict, expected: str):
    assert get_region_id(impact) == expected, expected


@pytest.mark.parametrize(
    'impact,expected',
    [
        ({}, None),
        ({'country': {'@id': ''}}, None),
        ({'country': {'@id': 'region-world'}}, 'region-world'),
        ({'country': {'@id': 'GADM-AUS'}}, 'GADM-AUS'),
        ({'site': {'country': {'@id': 'GADM-AUS'}}}, 'GADM-AUS'),
    ]
)
def test_get_country_id(impact: dict, expected: str):
    assert get_country_id(impact) == expected, expected
