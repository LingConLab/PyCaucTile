"""
Utility functions for the visualizations
"""
import pandas as pd
import matplotlib.colors as mcolors
import numpy as np
from typing import Union, List, Sequence, Dict


def _define_annotation_color(color: Union[str, List[str]]) -> np.ndarray:
    """
    Determine optimal text color (black or white) based on background color brightness for readability
 
    Parameters
    ----------
    color : str or list of str
        Background color(s) specified as hex codes (e.g., "#FF0000") or 
        matplotlib color names (e.g., "red"). Can be a single color or a list of colors
    
    Returns
    -------
    numpy.ndarray
        Array of text color codes: "#000000" (black) for light backgrounds,
        "#FFFFFF" (white) for dark backgrounds
    
    """
    if isinstance(color, str):
        color = [color]
        
    rgb_values = [np.array(mcolors.to_rgb(c)) * 255 for c in color]

    df = pd.DataFrame(rgb_values, columns=["red", "green", "blue"])

    brightness = (
        df["red"]   * 0.299 +
        df["green"] * 0.587 +
        df["blue"]  * 0.114
    )

    text_colors = np.where(brightness > 128, "#000000", "#FFFFFF")

    return text_colors


def _check_colors(colors: Sequence[str]) -> Dict[str, bool]:
    """
    Validate that each string in `colors` is a valid color specification.

    Parameters
    ----------
    colors : sequence of str
        Background color(s) specified as hex codes (e.g., "#FF0000") or 
        matplotlib color names (e.g., "red"). Can be a single color or a list of colors

    Returns
    -------
    dict
        Mapping {color: True/False} indicating whether each color is valid.
    """
    out: Dict[str, bool] = {}
    for c in colors:
        try:
            mcolors.to_rgb(c)
            out[c] = True
        except ValueError:
            out[c] = False
    return out
