from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.blank_node import is_run_required, get_total_value_converted_with_min_ratio
from hestia_earth.models.utils.product import liveweight_produced
from hestia_earth.models.utils.input import get_feed_inputs
from .. import MODEL
from . import feedConversionRatioCarbon
from . import feedConversionRatioDryMatter
from . import feedConversionRatioEnergy
from . import feedConversionRatioFedWeight
from . import feedConversionRatioNitrogen

MODELS = [
    feedConversionRatioCarbon,
    feedConversionRatioDryMatter,
    feedConversionRatioEnergy,
    feedConversionRatioFedWeight,
    feedConversionRatioNitrogen
]


def _practice(term_id: str, value: float):
    practice = _new_practice(term_id, MODEL)
    practice['value'] = [value]
    return practice


def _has_no_practice(term_id: str, cycle: dict):
    return find_term_match(cycle.get('practices', []), term_id, None) is None


def _run_model(cycle: dict, kg_liveweight: float, feed: float):
    def exec(model: dict):
        should_run = _has_no_practice(model.TERM_ID, cycle)
        return _practice(model.TERM_ID, model.run(cycle, feed) / kg_liveweight) if should_run else None
    return exec


def _run(cycle: dict, kg_liveweight: float, feed: float):
    return non_empty_list(map(_run_model(cycle, kg_liveweight, feed), MODELS))


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    kg_liveweight = liveweight_produced(products)
    feed = get_total_value_converted_with_min_ratio(MODEL, None, cycle, get_feed_inputs(cycle))

    should_run = all([kg_liveweight, feed])

    for model in MODELS:
        logRequirements(cycle, model=MODEL, term=model.TERM_ID,
                        kg_liveweight=kg_liveweight,
                        total_feed_in_MJ=feed)
        logShouldRun(cycle, MODEL, model.TERM_ID, should_run)

    return should_run, kg_liveweight, feed


def run(cycle: dict):
    run_required = any([is_run_required(MODEL, model.TERM_ID, cycle) for model in MODELS])
    should_run, kg_liveweight, feed = _should_run(cycle) if run_required else (False, None, None)
    return _run(cycle, kg_liveweight, feed) if should_run else []
