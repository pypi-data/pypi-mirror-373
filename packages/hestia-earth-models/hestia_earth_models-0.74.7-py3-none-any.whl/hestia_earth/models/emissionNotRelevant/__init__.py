from hestia_earth.schema import NodeType, EmissionMethodTier, TermTermType
from hestia_earth.utils.lookup import download_lookup, lookup_term_ids, lookup_columns, column_name
from hestia_earth.utils.lookup_utils import is_in_system_boundary
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.blank_node import _run_required, _run_model_required

REQUIREMENTS = {
    "Cycle": {
        "emissions": [{"@type": "Emission"}]
    }
}
RETURNS = {
    "Emission": [{
        "value": "0",
        "methodTier": "not relevant"
    }]
}
LOOKUPS = {
    "emission": [
        "term.id",
        "inHestiaDefaultSystemBoundary",
        "inputTermTypesAllowed",
        "productTermIdsAllowed",
        "productTermTypesAllowed",
        "siteTypesAllowed",
        "typesAllowed"
    ],
    "emission-model-productTermIdsAllowed": "",
    "emission-model-siteTypesAllowed": ""
}
MODEL = 'emissionNotRelevant'
TIER = EmissionMethodTier.NOT_RELEVANT.value


def _emission(term_id: str):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [0]
    emission['methodTier'] = TIER
    return emission


def _emission_ids():
    return lookup_term_ids(download_lookup(f"{TermTermType.EMISSION.value}.csv"))


def _model_ids(lookup_suffix: str):
    return [
        col for col in lookup_columns(download_lookup(f"emission-model-{lookup_suffix}.csv"))
        if col != column_name('term.id')
    ]


def _should_run_emission(cycle: dict, model_ids: list):
    def run(term_id: str):
        is_not_relevant = not _run_required(MODEL, term_id, cycle) or any([
            not _run_model_required(model_id, term_id, cycle, skip_logs=True) for model_id in model_ids
        ])
        in_system_boundary = is_in_system_boundary(term_id)

        should_run = all([is_not_relevant, in_system_boundary])
        if should_run:
            # no need to show the model failed
            logRequirements(cycle, model=MODEL, term=term_id,
                            is_not_relevant=is_not_relevant,
                            in_system_boundary=in_system_boundary,
                            run_required=False)
            logShouldRun(cycle, MODEL, term_id, should_run)
        return should_run
    return run


def _run(cycle: dict):
    emissions = _emission_ids()
    model_ids = list(set(flatten(map(_model_ids, ['productTermIdsAllowed', 'siteTypesAllowed']))))
    term_ids = list(filter(_should_run_emission(cycle, model_ids), emissions))
    return list(map(_emission, term_ids))


def _should_run(node: dict):
    node_type = node.get('@type', node.get('type'))

    logRequirements(node, model=MODEL,
                    node_type=node_type)

    should_run = node_type == NodeType.CYCLE.value
    logShouldRun(node, MODEL, None, should_run)
    return should_run


def run(_, node: dict): return _run(node) if _should_run(node) else []
