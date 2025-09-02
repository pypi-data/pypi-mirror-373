from hestia_earth.models.site.post_checks.country import run


def test_run():
    site = {'country': {'@type': 'Term', '@id': 'GADM-GBR', 'defaultProperties': []}}
    assert run(site) == {'country': {'@type': 'Term', '@id': 'GADM-GBR'}}
