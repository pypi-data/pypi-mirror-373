from hestia_earth.utils.model import linked_node

REQUIREMENTS = {
    "Cycle": {
        "otherSites": [{
            "@type": "Site",
            "@id": ""
        }]
    }
}
RETURNS = {
    "Cycle": {
        "otherSites": [{"@type": "Site"}]
    }
}
MODEL_KEY = 'otherSites'


def _run_site(site: dict): return linked_node(site)


def _should_run_site(site: dict): return site.get('@id') is not None


def _should_run(cycle: dict): return len(cycle.get(MODEL_KEY, [])) > 0


def run(cycle: dict):
    return cycle | (
        ({
            MODEL_KEY: [_run_site(site) if _should_run_site(site) else site for site in cycle.get(MODEL_KEY, [])]
        }) if _should_run(cycle) else {}
    )
