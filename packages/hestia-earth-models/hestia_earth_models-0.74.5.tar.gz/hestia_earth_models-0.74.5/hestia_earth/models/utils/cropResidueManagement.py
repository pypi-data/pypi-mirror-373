from .term import get_crop_residue_management_terms


def has_residue_incorporated_practice(cycle: dict):
    all_terms = get_crop_residue_management_terms()
    terms = [term_id for term_id in all_terms if term_id.startswith('residueIncorporated')]
    return any([p for p in cycle.get('practices', []) if p.get('term', {}).get('@id') in terms])
