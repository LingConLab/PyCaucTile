"""
PyCaucTile: A package for generating tile grid maps of East Caucasian languages

Features:
- 

License: GPL-3.0 
"""

__version__ = "0.1.0"
__license__ = "GPL-3.0"

from .ec_languages import load_ec_languages, ec_languages
from .ec_tile_map import ec_tile_map, ec_template, ec_tile_numeric, ec_tile_categorical
from .utils import define_annotation_color

# from pycauctile import *
__all__ = [
    'ec_tile_map',
    'ec_template',
    'ec_tile_numeric',
    'ec_tile_categorical',
    'define_annotation_color',
    'load_ec_languages',
    'ec_languages',
    '__version__',
    '__license__'
]