"""
Utility functions for the visualizations
"""
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from typing import Union, List, Sequence, Dict


def _define_annotation_color(color: Union[str, Sequence[str]]) -> np.ndarray:
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
    

def _palette_from_cmap(name: str, n: int, reverse: bool = False) -> List[str]:
    
    if n <= 0:
        raise ValueError("`n` must be a positive integer.")
    
    cmap = _get_cmap(name)  

    # qualitative colormap -> colors in their defined order
    if hasattr(cmap, "colors") and cmap.colors is not None:
        base = [mcolors.to_hex(c, keep_alpha=False) for c in cmap.colors]
        if reverse:
            base = base[::-1]

        # fewer colors
        if n <= len(base):
            return base[:n]

        # more colors
        out = []
        while len(out) < n:
            out.extend(base)
        return out[:n]

    # continuous colormap
    if reverse:
        cmap = cmap.reversed()

    xs = np.linspace(0, 1, n) if n > 1 else [0.5]
    return [mcolors.to_hex(cmap(x), keep_alpha=False) for x in xs]


def _get_cmap(name: str):
    """
    Return a matplotlib colormap by name with version compatibility.

    Parameters
    ----------
    name : str
        Name of a matplotlib colormap.

    Returns
    -------
    matplotlib.colors.Colormap
        The requested colormap.

    Raises
    ------
    ValueError
        If the colormap name is unknown.
    """
    try:
        if hasattr(matplotlib, "colormaps"):
            # matplotlib >= 3.7
            return matplotlib.colormaps.get_cmap(name)
        # matplotlib < 3.7
        return cm.get_cmap(name)
    except ValueError as e:
        raise ValueError(
            f"Unknown colormap '{name}'. Pass a valid matplotlib colormap name "
            "(e.g. 'viridis', 'Blues', or 'Set2')."
        ) from e