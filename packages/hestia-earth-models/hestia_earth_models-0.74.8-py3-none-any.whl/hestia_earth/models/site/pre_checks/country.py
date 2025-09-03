from hestia_earth.schema import TermTermType

from hestia_earth.models.utils.term import download_term


def run(site: dict): return site | {'country': download_term(site.get('country', {}).get('@id'), TermTermType.REGION)}
