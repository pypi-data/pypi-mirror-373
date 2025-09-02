from hestia_earth.utils.model import linked_node


def run(site: dict): return site | {'country': linked_node(site.get('country'))}
