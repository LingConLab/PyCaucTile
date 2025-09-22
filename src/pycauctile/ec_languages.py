"""
This module provides loading utilities for the built-in East Caucasian languages dataset
"""

import pandas as pd
import importlib.resources
import os


def load_ec_languages() -> pd.DataFrame:
    """
    Attempt to load the language data from the package resources
    using multiple methods for compatibility across Python versions
    
    Returns
    -------
    pandas.DataFrame
    DataFrame containing information about East Caucasian languages
    
    Raises
    ------
    FileNotFoundError
        If the data file cannot be found in any of the expected locations
    
    Examples
    --------
    >>> from pycauctile.ec_languages import load_ec_languages
    >>> languages_df = load_ec_languages()
    >>> print(languages_df.head())
    """
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
            try:
                return pd.read_csv(data_path)
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Could not find ec_languages.csv "
                )



# load the data once when module is imported
ec_languages = load_ec_languages()