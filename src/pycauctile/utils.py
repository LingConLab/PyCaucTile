import pandas as pd
import matplotlib.colors as mcolors
import numpy as np


def define_annotation_color(color):
    rgb_values = [np.array(mcolors.to_rgb(c)) * 255 for c in color]

    df = pd.DataFrame(rgb_values, columns=["red", "green", "blue"])

    brightness = (
        df["red"]   * 0.299 +
        df["green"] * 0.587 +
        df["blue"]  * 0.114
    )

    text_colors = np.where(brightness > 160, "#000000", "#E5E5E5")

    return text_colors
