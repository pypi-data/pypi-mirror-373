import sys
from importlib import import_module
from os.path import dirname, abspath

from hestia_earth.models.utils.blank_node import run_if_required

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
MODEL = 'environmentalFootprintV3-1'
MODEL_FOLDER = MODEL.replace('-', '_')
PKG = '.'.join(['hestia_earth', 'models', MODEL_FOLDER])


def run(model: str, data): return run_if_required(MODEL, model, data, import_module(f".{model}", package=PKG))
