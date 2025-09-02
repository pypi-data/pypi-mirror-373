from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_blank_nodes_id
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.blank_node import get_total_value
from .utils import _practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "practices": [{
            "@type": "Practice",
            "term.@id": ["residueBurnt", "residueLeftOnField", "residueRemoved"],
            "added": ["value"],
            "model.@id": "koble2014"
        }]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
MODEL_KEY = 'cropResidueManagement'
MODEL_LOG = '/'.join([MODEL, MODEL_KEY])


def _is_recalculated(practice: dict):
    return practice.get('model', {}).get('@id') == MODEL and is_from_model(practice)


def _run_practice(cycle: dict, ratio: float, practice: dict):
    term = practice.get('term', {})
    value = list_sum(practice.get('value', [0]))
    logRequirements(cycle, model=MODEL,
                    rescale_ratio=ratio,
                    value_before_rescale=value)
    logShouldRun(cycle, MODEL, term.get('@id'), True)
    return _practice(term, round(value * ratio, 7))


def _run(cycle: dict):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    recalculated_practices = list(filter(_is_recalculated, practices))
    recalculated_total = list_sum(get_total_value(recalculated_practices))
    non_recalculated_total = list_sum(get_total_value([p for p in practices if not _is_recalculated(p)]))
    ratio = (100-non_recalculated_total) / recalculated_total
    return [_run_practice(cycle, ratio, p) for p in recalculated_practices]


def _should_run(cycle: dict):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    recalculated_practices = list(filter(_is_recalculated, practices))
    recalculated_total_value = list_sum(get_total_value(recalculated_practices))
    total_value = list_sum(get_total_value(practices))

    logRequirements(cycle, model=MODEL_LOG,
                    total_value=total_value,
                    recalculated_total_value=recalculated_total_value,
                    recalculated_practice_ids=log_blank_nodes_id(recalculated_practices))

    should_run = all([total_value > 0, total_value != 100, recalculated_total_value > 0])
    logShouldRun(cycle, MODEL_LOG, None, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
