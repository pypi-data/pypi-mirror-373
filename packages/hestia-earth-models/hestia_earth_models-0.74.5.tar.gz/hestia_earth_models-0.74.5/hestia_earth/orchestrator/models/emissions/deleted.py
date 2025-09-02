from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.emission import emissions_in_system_boundary


def _run_emission(term_ids: list):
    def run(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        return (emission | {'deleted': True}) if term_id not in term_ids else None
    return run


def run(_models: list, cycle: dict):
    emission_ids = emissions_in_system_boundary()
    emissions = cycle.get('emissions', [])
    return non_empty_list(map(_run_emission(emission_ids), emissions)) if len(emission_ids) > 0 else []
