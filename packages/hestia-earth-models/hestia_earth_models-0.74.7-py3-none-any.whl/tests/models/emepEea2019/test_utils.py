import pytest

from hestia_earth.models.emepEea2019.utils import should_run_animal, _duration_in_housing

class_path = 'hestia_earth.models.emepEea2019.utils'
TERMS = [
    'diesel',
    'petrol'
]


@pytest.mark.parametrize(
    "test_name,cycle,expected_duration",
    [
        (
            "no sites => 0",
            {"completeness": {"@type": "Completeness", "animalPopulation": False}},
            0
        ),
        (
            "site and other sites have wrong type => 0",
            {
                "site": {"@type": "Site", "siteType": "permanent pasture"},
                "siteDuration": 15,
                "otherSites": [
                    {"@type": "Site", "siteType": "pond"},
                    {"@type": "Site", "siteType": "pond"},
                    {"@type": "Site", "siteType": "pond"},
                ],
                "otherSitesDuration": [20, 21, 22],
            },
            0
        ),
        (
            "only second other site is animal housing => 12",
            {
                "site": {"@type": "Site", "siteType": "pond"},
                "siteDuration": 20,
                "otherSites": [
                    {"@type": "Site", "siteType": "pond"},
                    {"@type": "Site", "siteType": "animal housing"},
                    {"@type": "Site", "siteType": "pond"},
                ],
                "otherSitesDuration": [11, 12, 13],
            },
            12
        ),
        (
            "only site is animal housing => 20",
            {
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [
                    {"@type": "Site", "siteType": "forest"},
                    {"@type": "Site", "siteType": "forest"},
                    {"@type": "Site", "siteType": "forest"},
                ],
                "siteDuration": 20,
                "otherSitesDuration": [12, 13, 14],
            },
            20
        ),
        (
            "site and otherSites are animal housing, sum all values => 59",
            {
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [
                    {"@type": "Site", "siteType": "animal housing"},
                    {"@type": "Site", "siteType": "animal housing"},
                    {"@type": "Site", "siteType": "animal housing"},
                ],
                "siteDuration": 20,
                "otherSitesDuration": [12, 13, 14],
            },
            59
        )

    ]
)
def test_duration_in_housing(test_name, cycle, expected_duration):
    assert _duration_in_housing(cycle) == expected_duration


@pytest.mark.parametrize(
    "test_name,cycle,expected_should_run",
    [
        (
            "not complete => no run",
            {"completeness": {"@type": "Completeness", "animalPopulation": False}},
            False
        ),
        (
            "no site or other sites => no run",
            {"completeness": {"@type": "Completeness", "animalPopulation": True}},
            False
        ),
        (
            "no site or other sites with 'animal housing' type => no run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "permanent pasture"},
                "otherSites": [{"@type": "Site", "siteType": "pond"}]
            },
            False
        ),
        (
            "no site or other sites with 'animal housing' type and duration => no run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [{"@type": "Site", "siteType": "pond"}],
                "siteDuration": ""
            },
            False
        ),
        (
            "no animal values => no run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [{"@type": "Site", "siteType": "pond"}],
                "siteDuration": 150,
                "animals": [
                    {"value": ""}
                ]
            },
            False
        ),
        (
            "animal values reference period is not 'average' => no run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [{"@type": "Site", "siteType": "pond"}],
                "siteDuration": 150,
                "animals": [
                    {
                        "@type": "Animal",
                        "value": 1
                    },
                    {
                        "@type": "Animal",
                        "value": 2,
                        "referencePeriod": ""
                    },
                    {
                        "@type": "Animal",
                        "value": 3,
                        "referencePeriod": "start of Cycle"
                    },
                ]
            },
            False
        ),
        (
            "missing otherSitesDuration => no run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "animal housing"},
                "otherSites": [{"@type": "Site", "siteType": "pond"}],
                "siteDuration": 150,
                "animals": [
                    {
                        "@type": "Animal",
                        "value": 2,
                        "referencePeriod": ""
                    },
                    {
                        "@type": "Animal",
                        "value": 3,
                        "referencePeriod": "average"
                    },
                ]
            },
            False
        ),
        (
            "all requirements met with otherSites => run",
            {
                "completeness": {"@type": "Completeness", "animalPopulation": True},
                "site": {"@type": "Site", "siteType": "pond"},
                "siteDuration": "",
                "otherSites": [{"@type": "Site", "siteType": "animal housing"}],
                "otherSitesDuration": [200],
                "animals": [
                    {
                        "@type": "Animal",
                        "value": 2,
                        "referencePeriod": ""
                    },
                    {
                        "@type": "Animal",
                        "value": 3,
                        "referencePeriod": "average"
                    },
                ]
            },
            True
        ),

    ]
)
def test_should_run_animal(test_name, cycle, expected_should_run):
    should_run, *args = should_run_animal(cycle, 'model', 'term', 'tier')
    assert should_run == expected_should_run, test_name
