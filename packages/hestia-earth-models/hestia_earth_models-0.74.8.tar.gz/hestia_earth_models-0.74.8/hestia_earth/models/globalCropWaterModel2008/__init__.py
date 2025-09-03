from os.path import dirname, abspath
import sys
from importlib import import_module

from hestia_earth.models.utils.blank_node import run_if_required

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
MODEL = 'globalCropWaterModel2008'
PKG = '.'.join(['hestia_earth', 'models', MODEL])


def run(model: str, data): return run_if_required(MODEL, model, data, import_module(f".{model}", package=PKG))
