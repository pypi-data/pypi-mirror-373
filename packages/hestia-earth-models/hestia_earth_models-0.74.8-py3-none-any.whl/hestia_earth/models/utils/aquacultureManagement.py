from .site import WATER_TYPES, valid_site_type as site_valid_site_type


def valid_site_type(cycle: dict): return site_valid_site_type(cycle.get('site', {}), WATER_TYPES)
