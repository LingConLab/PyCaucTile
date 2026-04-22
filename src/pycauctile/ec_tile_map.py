"""
This module provides main PyCaucTile functions to create tile grid map visualizations 
for East Caucasian language features using plotnine
"""
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from typing import Optional, Union, Dict, List, Sequence
from plotnine import (
    ggplot, aes, geom_tile, geom_text, theme_void, 
    scale_fill_manual, scale_color_manual, scale_fill_gradientn, scale_color_identity, 
    labs, theme, element_text, element_blank, guides, guide_legend, guide_colorbar
)

try:
    from .ec_languages import ec_languages
    from .utils import _define_annotation_color, _check_colors, _palette_from_cmap
except ImportError:
    # development fallback
    from ec_languages import ec_languages
    from utils import _define_annotation_color, _check_colors, _palette_from_cmap


def ec_tile_map(
      data: Optional[pd.DataFrame] = None,
      feature_column: str = "feature",
      title: Optional[str] = None,
      title_position: str = "left",
      annotate_feature: bool = False,
      abbreviation: bool = True,
      hide_languages: Optional[List[str]]=None,
      rename_languages: Optional[Union[Dict[str, str], pd.DataFrame]] = None,
      tile_colors: Optional[Union[str, Sequence[str]]] = None, 
      palette_reverse: bool = False
  ):
      """
        Create a tile grid map visualization for East Caucasian language features
        
        Parameters
        ----------
        data : pandas.DataFrame, optional
            DataFrame containing language feature data. Must include a 'language' column
            and the feature column specified by `feature_column`
        feature_column : str, default "feature"
            Name of the column containing linguistic feature values to visualize
        title : str, optional
            Title to display above the visualization
        title_position : str, default "left"
            Horizontal position of the title: "left", "center", or "right"
        annotate_feature : bool, default False
            If True, displays feature values as text annotations on the tiles
        abbreviation : bool, default True
            If True, uses language abbreviations instead of full names
        hide_languages : list of str, optional
            List of language names to exclude from the visualization
        rename_languages : dict or pandas.DataFrame, optional
            Mapping to rename languages. Can be a dictionary {old_name: new_name}
            or DataFrame with 'language' and 'new_language_name' columns
        
        Returns
        -------
        plotnine.ggplot
            A ggplot object that can be displayed, customized, or saved to file
        
        Examples
        --------
        >>> from pycauctile import ec_tile_map, ec_languages
        >>> 
        >>> basic_map = ec_tile_map()
        >>> 
        >>> feature_map = ec_tile_map(
        ...     data=ec_languages,
        ...     feature_column="consonant_inventory_size",
        ...     title="Consonant Inventory Size",
        ...     annotate_feature=True
        ... )
      """
      # arguments check 

      # Title
      if title is not None and not isinstance(title, str):
          raise ValueError("The argument `title` must be a string or None.")

      # Title position
      if not isinstance(title_position, str):
          raise ValueError(
              "The argument `title_position` must be a string."
          )

      if title_position not in ('left', 'center', 'right'):
          raise ValueError(
              "The argument `title_position`  must be one of: 'left', 'center', 'right'."
          )

      # Annotate feature
      if not isinstance(annotate_feature, bool):
          raise ValueError("The argument `annotate_feature` must be a boolean.")

      # Abbreviation
      if not isinstance(abbreviation, bool):
          raise ValueError("The argument `abbreviation` must be a boolean.")

      # Hide languages
      if hide_languages is not None:
          if not all(lang in ec_languages["language"].tolist() for lang in hide_languages):
              raise ValueError(
                  "The argument `hide_languages` must be a list of language names, see 'ec_languages['language']' for the possible values."
              )

      # Rename languages
      if rename_languages is not None:
          is_named_vector = isinstance(rename_languages, dict)
          is_valid_df = (
              isinstance(rename_languages, pd.DataFrame)
              and all(col in rename_languages.columns for col in ["language", "new_language_name"])
          )

          if not (is_named_vector or is_valid_df):
              raise ValueError(
                  "The argument `rename_languages` must be either a dict or a pandas DataFrame with columns `language` and `new_language_name`."
              )

      if isinstance(rename_languages, pd.DataFrame):
          if not ("language" in rename_languages.columns and "new_language_name" in rename_languages.columns):
              raise ValueError(
                  "The argument `rename_languages` must contain columns `language` and `new_language_name`."
              )
          if not all(lang in ec_languages["language"].tolist() for lang in rename_languages["language"]):
              raise ValueError(
                  "Invalid values in `rename_languages['language']`, see 'ec_languages['language']' for the possible values.."
              )
      elif isinstance(rename_languages, dict):
          if not all(name in ec_languages["language"].tolist() for name in rename_languages.keys()):
              raise ValueError(
                  "Invalid keys in `rename_languages`, see 'ec_languages['language']' for the possible values.."
              )

      # palette_reverse
      if not isinstance(palette_reverse, bool):
          raise ValueError("The argument `palette_reverse` must be a boolean.")

      # restructure rename_languages 

      if isinstance(rename_languages, dict):
          rename_languages = pd.DataFrame({
              "new_language_name": list(rename_languages.values()),
              "language": list(rename_languages.keys())
          })

      # redefine title_position 

      if title_position == "left":
          title_position = 0
      elif title_position == "center":
          title_position = 0.5
      elif title_position == "right":
          title_position = 1

      # ec_template() assignment 

      if data is None:
          return ec_template(
              title=title,
              title_position=title_position,
              abbreviation=abbreviation
          )
      else:

          # arguments check 

          if not isinstance(data, pd.DataFrame):
              raise ValueError("`data` must be a pandas DataFrame.")
          if "language" not in data.columns:
              raise ValueError("`data` must contain a `language` column.")
          if feature_column not in data.columns:
              raise ValueError(
                  f"`data` must contain the feature column '{feature_column}'. If you have a column with a different name, please, use the argument 'feature_column' to provide it."
              )
          # !! just a string
          if not isinstance(feature_column, str):
              raise ValueError("The argument 'feature_column' must be a string.")
        

          # rename the user feature column before merge
          data2 = data.copy()
          data2 = data2.rename(columns={feature_column: "feature"})

          # merge EC dataset with data provided by a user
          for_plot = ec_languages.copy()   # keep ec_languages order
          for_plot = for_plot.merge(data2, on="language", how="left", suffixes=("", "_y"))

          # drop accidental duplicate columns from user data
          cols_to_drop = [col for col in for_plot.columns if col.endswith("_y")]
          for_plot = for_plot.drop(columns=cols_to_drop)

          # for missing colors
          if "language_color" in for_plot.columns:
              for_plot["language_color"] = for_plot["language_color"].fillna("#E5E5E5")
          else:
              for_plot["language_color"] = "#E5E5E5"

          # rename languages 

          if rename_languages is not None:
              for_plot = for_plot.merge(rename_languages, on="language", how="left")
              for_plot["language"] = for_plot["new_language_name"].combine_first(for_plot["language"])
              for_plot["abbreviation"] = for_plot["new_language_name"].combine_first(for_plot["abbreviation"])
              for_plot = for_plot.drop(columns=["new_language_name"])

          # hide languages 

          if hide_languages is not None:
              for_plot = for_plot[~for_plot["language"].isin(hide_languages)]


          # add an 'alpha' column for the cases when there are NAs in data 
          for_plot["alpha"] = for_plot["feature"].apply(lambda x: 0.2 if pd.isna(x) else 1)

          # change labels to abbreviations 

          if abbreviation:
              for_plot["language"] = for_plot.apply(
                  lambda row: row["abbreviation"] if pd.notna(row["abbreviation"]) else row["language"],
                  axis=1
              )

          # add feature values to the language names 

          if annotate_feature:
              for_plot["language"] = for_plot.apply(
                  lambda row: f"{row['language']}\n{row['feature']}" if pd.notna(row["feature"]) else row["language"],
                  axis=1
              )

          # ec_tile_numeric() or ec_tile_categorical() 

          if pd.api.types.is_numeric_dtype(for_plot["feature"]):
              return ec_tile_numeric(
                  data=for_plot,
                  title=title,
                  title_position=title_position,
                  annotate_feature=annotate_feature,
                  abbreviation=abbreviation,
                  tile_colors=tile_colors,
                  palette_reverse=palette_reverse
              )
          else:
              return ec_tile_categorical(
                  data=for_plot,
                  title=title,
                  title_position=title_position,
                  annotate_feature=annotate_feature,
                  abbreviation=abbreviation,
                  tile_colors=tile_colors,
                  palette_reverse=palette_reverse
              )


def ec_template(
    title: Optional[str], 
    title_position: float, 
    abbreviation: bool
    ):
    """
    Create a template tile map showing language coords and colors without feature data
    
    Parameters
    ----------
    title : str, optional
        Title for the visualization
    title_position : str
        Horizontal position of the title: "left", "center", or "right"
    abbreviation : bool
        If True, uses language abbreviations instead of full names
    
    Returns
    -------
    plotnine.ggplot
        A template ggplot object showing language positions
    """

    # load data 
    for_plot = ec_languages.copy()

    # add a 'text_color' column for the text colors 
    for_plot["text_color"] = _define_annotation_color(for_plot["language_color"])

    # create a factor for correct coloring in ggplot 
    for_plot["language_color"] = pd.Categorical(
        for_plot["language_color"],
        categories=list(for_plot["language_color"]),
        ordered=True
    )

    # change labels to abbreviations 
    if abbreviation:
        for_plot["language"] = for_plot.apply(
            lambda r: r["language"] if pd.isna(r["abbreviation"]) else r["abbreviation"],
            axis=1
        )

    # create a map 
    p = (
        ggplot(for_plot, aes("x", "y"))
        + geom_tile(aes(fill="language_color"), show_legend=False)
        + geom_text(aes(label="language", color="text_color"), show_legend=False, size = 5.3)
        + theme_void()
        + scale_fill_manual(values=list(ec_languages["language_color"]))
        + scale_color_manual(values=["black", "white"])
        + labs(color=None, title=title)
        + theme(plot_title=element_text(hjust=title_position))
    )

    return p


def ec_tile_categorical(
    data, 
    title: Optional[str], 
    title_position: float, 
    annotate_feature: bool, 
    abbreviation: bool,
    tile_colors: Optional[Union[str, Sequence[str]]] = None,
    palette_reverse: bool = False
    ):
    """
    Create a tile map for categorical feature data with discrete color coding
    
    Parameters
    ----------
    data : pandas.DataFrame
        Prepared data for visualization
    title : str, optional
        Title for the visualization
    title_position : str
        Horizontal position of the title: "left", "center", or "right"
    annotate_feature : bool
        Whether to annotate feature values on tiles
    abbreviation : bool
        Whether to use language abbreviations
    
    Returns
    -------
    plotnine.ggplot
        A ggplot object with categorical feature visualization
    """    
    # load data 
    for_plot = data.copy()

    # type safety for correct mapping
    for_plot["feature"] = for_plot["feature"].astype("string")
    
    levels = sorted(for_plot["feature"].dropna().unique().tolist())
    n_levels = len(levels)

    # default simple palettes
    if n_levels > 10:
        default_palette = 'Set3'
    else:
        default_palette = 'Set2'


    # default palette
    if tile_colors is None:
        palette = _palette_from_cmap(default_palette, n_levels)

    # name of palette
    elif isinstance(tile_colors, str):
        palette = _palette_from_cmap(tile_colors, n_levels, reverse=palette_reverse)

    # list of colors
    elif isinstance(tile_colors, (list, tuple)):
        checks = _check_colors(tile_colors)
        wrong_names = [c for c, ok in checks.items() if not ok]
        if wrong_names:
            raise ValueError(
                "Invalid color names in `tile_colors`: " + ", ".join(wrong_names)
            )

        if len(tile_colors) != n_levels:
            raise ValueError(
                f"`tile_colors` must contain exactly {n_levels} colors for this feature."
            )

        if palette_reverse:
            palette = list(tile_colors)[::-1] 
        else:
            palette = list(tile_colors)

    else:
        raise ValueError(
            "`tile_colors` must be None, a colormap name, or a list/tuple of colors."
        )
    

    # map colors to feature values
    value_color_map = dict(zip(levels, palette))
    for_plot["tile_color"] = for_plot["feature"].map(value_color_map)
    # NA tiles 
    for_plot["tile_color"] = for_plot["tile_color"].fillna("#E5E5E5")
    
    for_plot["text_color"] = _define_annotation_color(for_plot["tile_color"])

    
    # create a map
    p = (
        ggplot(for_plot, aes("x", "y", alpha="alpha"))
        # base grey tiles
        + geom_tile(aes(alpha="alpha"), size=0, color="#E5E5E5", fill="#E5E5E5")
        # colored tiles only for non-NA
        + geom_tile(aes(fill="feature"), size=0)
        + geom_text(aes(label="language", color="text_color"), size=5.3, show_legend=False)
        + theme_void()
        + labs(title=title)  

        + theme(
            legend_position="bottom",
            plot_title=element_text(hjust=title_position, size=6.3),
            legend_text=element_text(size=5.3),
            legend_title=element_blank()  
        )
        # discrete legend
        + guides(alpha="none", fill=guide_legend(title=None), color="none")  
        + scale_color_identity()
        + scale_fill_manual(values=value_color_map, na_value="#E5E5E5", na_translate=False)
    )

    return p


def ec_tile_numeric(
    data, 
    title: Optional[str], 
    title_position: float, 
    annotate_feature: bool, 
    abbreviation: bool,
    tile_colors: Optional[Union[str, Sequence[str]]] = None,
    palette_reverse: bool = False
    ):
    """
    Create a tile map for numerical feature data with a gradient color scale
    
    Parameters
    ----------
    data : pandas.DataFrame
        Prepared data for visualization
    title : str, optional
        Title for the visualization
    title_position : str
        Horizontal position of the title: "left", "center", or "right"
    annotate_feature : bool
        Whether to annotate feature values on tiles
    abbreviation : bool
        Whether to use language abbreviations
    
    Returns
    -------
    plotnine.ggplot
        A ggplot object with numerical feature visualization
    """    
    # load data 
    for_plot = data.copy()

    # type safety (+ try coercing) 
    for_plot["feature"] = pd.to_numeric(for_plot["feature"], errors="coerce")

    default_palette = 'Blues'


    # default palette
    if tile_colors is None:
        palette = _palette_from_cmap(default_palette, 256, reverse=palette_reverse)

    # name of palette     
    elif isinstance(tile_colors, str):
        palette = _palette_from_cmap(tile_colors, 256, reverse=palette_reverse)

    # list of colors        
    elif isinstance(tile_colors, (list, tuple)) and len(tile_colors) in (2, 3):
        checks = _check_colors(tile_colors)
        wrong_names = [c for c, ok in checks.items() if not ok]
        if wrong_names:
            raise ValueError(
                "Invalid color names in `tile_colors`: " + ", ".join(wrong_names)
            )

        if palette_reverse:
            palette = list(tile_colors[::-1]) 
        else: 
            palette = list(tile_colors)
    
    else:
        raise ValueError(
            "`tile_colors` must be None, a colormap name, or a list/tuple of 2 or 3 colors."
        )  

    # NA tiles
    for_plot["tile_color"] = "#E5E5E5"
    for_plot["text_color"] = "#000000"

    for_plot_non_na = for_plot["feature"].notna()
    
    if for_plot_non_na.any():
        vals = for_plot.loc[for_plot_non_na, "feature"].astype(float).to_numpy()
        vmin = float(np.nanmin(vals))
        vmax = float(np.nanmax(vals))

        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        cmap_local = mcolors.LinearSegmentedColormap.from_list("tile_numeric", palette)

        for_plot.loc[for_plot_non_na, "tile_color"] = [mcolors.to_hex(cmap_local(norm(v))) for v in vals]

        for_plot.loc[for_plot_non_na, "text_color"] = _define_annotation_color(for_plot.loc[for_plot_non_na, "tile_color"])
 

    # create a map 
    p = (
        ggplot(for_plot, aes("x", "y", alpha="alpha"))
        # base grey tiles
        + geom_tile(aes(alpha="alpha"), size=0, color="#E5E5E5", fill="#E5E5E5")
        # colored tiles only for non-NA
        + geom_tile(aes(fill="feature"))
        + geom_text(aes(label="language", color="text_color"), size=5.3, show_legend=False)
        + theme_void()
        + labs(title=title) 
        + theme(
            legend_position="bottom",
            plot_title=element_text(hjust=title_position, size=6.3),
            legend_text=element_text(size=5.3),
            legend_title=element_blank() 
        )
        # continuous legend
        + guides(alpha="none", fill=guide_colorbar(title=None))
        + scale_color_identity()
        + scale_fill_gradientn(colors=palette, na_value="#E5E5E5")
    )

    return p