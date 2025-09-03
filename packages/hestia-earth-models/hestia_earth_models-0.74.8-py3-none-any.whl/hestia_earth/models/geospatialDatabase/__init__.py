from os import listdir
from os.path import dirname, abspath
import sys
from importlib import import_module

from hestia_earth.models.utils.blank_node import run_if_required

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
MODEL = 'geospatialDatabase'
PKG = '.'.join(['hestia_earth', 'models', MODEL])


def run(model: str, data): return run_if_required(MODEL, model, data, import_module(f".{model}", package=PKG))


def _load_ee_params(filename: str):
    term = filename.replace('.py', '')
    module = import_module(f".{term}", package=PKG)
    return {'name': term, 'params': getattr(module, 'EE_PARAMS', None)}


def _valid_ee_params(data: dict): return data.get('params') is not None


def list_ee_params():
    files = listdir(CURRENT_DIR)
    files = sorted([f for f in files if f.endswith('.py') and not f.startswith('_')])
    values = list(map(_load_ee_params, files))
    return list(filter(_valid_ee_params, values))
