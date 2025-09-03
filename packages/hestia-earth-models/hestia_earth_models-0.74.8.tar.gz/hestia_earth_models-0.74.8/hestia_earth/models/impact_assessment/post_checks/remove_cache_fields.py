def run(impact: dict):
    cache_keys = [key for key in impact.keys() if key.startswith('cache')]
    for key in cache_keys:
        del impact[key]
        try:
            impact['added'].remove(key)
        except Exception:
            continue
    return impact
