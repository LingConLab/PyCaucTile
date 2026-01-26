"""
PyCaucTile: A package for generating tile grid maps of East Caucasian languages

Features:
to be written

License: GPL-3.0 
"""

__version__ = "1.0.0"
__license__ = "GPL-3.0"

from .ec_languages import load_ec_languages, ec_languages
from .ec_tile_map import ec_tile_map, ec_template, ec_tile_numeric, ec_tile_categorical


# from pycauctile import *
__all__ = [
    'ec_tile_map',
    'ec_template',
    'ec_tile_numeric',
    'ec_tile_categorical',
    'load_ec_languages',
    'ec_languages',
    '__version__',
    '__license__'
]