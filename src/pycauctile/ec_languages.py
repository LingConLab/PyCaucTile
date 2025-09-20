import pandas as pd
import importlib.resources
from typing import Optional
import os


def load_ec_languages():

    try:
        # modern approach, Python 3.9+ is required
        with importlib.resources.files("pycauctile.data").joinpath("ec_languages.csv").open() as f:
            return pd.read_csv(f)
    except (AttributeError, ModuleNotFoundError, FileNotFoundError):
        # fallback for older Python versions
        try:
            with importlib.resources.open_text("pycauctile.data", "ec_languages.csv") as f:
                return pd.read_csv(f)
        except (FileNotFoundError, ModuleNotFoundError):
            # development fallback
            current_dir = os.path.dirname(__file__)
            data_path = os.path.join(current_dir, 'data', 'ec_languages.csv')
            return pd.read_csv(data_path)


# load the data once when module is imported
ec_languages = load_ec_languages()