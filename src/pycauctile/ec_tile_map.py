"""
This module provides main PyCaucTile functions to create tile grid map visualizations 
for East Caucasian language features using plotnine
"""
import pandas as pd
from typing import Optional, Union, Dict, List
from plotnine import (
    ggplot, aes, geom_tile, geom_text,
    theme_void, scale_fill_manual, scale_color_manual, scale_fill_discrete,
    scale_fill_distiller, scale_fill_gradient, scale_fill_brewer,
    labs, theme, element_text, element_blank, guides, guide_legend
)

try:
    from .ec_languages import ec_languages
    from .utils import define_annotation_color
except ImportError:
    # development fallback
    from ec_languages import ec_languages
    from utils import define_annotation_color



# load the data from directory
# ec_languages = pd.read_csv("data/ec_languages.csv")


def ec_tile_map(
      data=None,
      feature_column="feature",
      title=None,
      title_position="left",
      annotate_feature=False,
      abbreviation=True,
      hide_languages=None,
      rename_languages=None,
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
          raise ValueError("The argument 'title' should be a character vector with one value")

      # Title position
      if not isinstance(title_position, str):
          raise ValueError(
              "The argument 'title_position' should be a character vector with one of the following values: 'left', 'center', or 'right'"
          )

      if title_position not in ('left', 'center', 'right'):
          raise ValueError(
              "The argument 'title_position' should be a character vector with one of the following values: 'left', 'center', or 'right'"
          )

      # Annotate feature
      if not isinstance(annotate_feature, bool):
          raise ValueError("The argument 'annotate_feature' should be a logical vector with one value")

      # Abbreviation
      if not isinstance(abbreviation, bool):
          raise ValueError("The argument 'abbreviation' should be a logical vector with one value")

      # Hide languages
      if hide_languages is not None:
          if not all(lang in ec_languages["language"].tolist() for lang in hide_languages):
              raise ValueError(
                  "The argument 'hide_languages' should be a character vector with languages, see 'ec_languages$language' for the possible values"
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
                  "The argument 'rename_languages' should be either a named character vector with languages as a name or dataframe with columns 'language' and 'new_language_name', see 'ec_languages$language' for the possible values"
              )

      if isinstance(rename_languages, pd.DataFrame):
          if not ("language" in rename_languages.columns and "new_language_name" in rename_languages.columns):
              raise ValueError(
                  "The argument 'rename_languages' should be either a named character vector with languages as a name or dataframe with columns 'language' and 'new_language_name', see 'ec_languages$language' for the possible values"
              )
          if not all(lang in ec_languages["language"].tolist() for lang in rename_languages["language"]):
              raise ValueError(
                  "The 'language' column in 'rename_languages' contains unexpected values, see 'ec_languages$language' for the possible values"
              )
      elif isinstance(rename_languages, dict):
          if not all(name in ec_languages["language"].tolist() for name in rename_languages.keys()):
              raise ValueError(
                  "The names in 'rename_languages' contain unexpected values, see 'ec_languages$language' for the possible values"
              )

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
              raise ValueError("Data should be a dataframe")
          if "language" not in data.columns:
              raise ValueError("Data should contain column 'language'")
          if feature_column not in data.columns:
              raise ValueError(
                  "Data should contain column 'feature'. If you have a column with a different name, please, use the argument 'feature_column' to provide it."
              )
          # !! just a string
          if not isinstance(feature_column, str):
              raise ValueError("The argument 'feature_column' should be a character vector with one value")
          
          # merge EC dataset with data provided by a user
          for_plot = ec_languages.copy() # copy to keep ec_languages order
          for_plot = for_plot.merge(data, on="language", how="left", suffixes=("", "_y"))

          for_plot = for_plot.rename(columns={feature_column: "feature"})

          # delete with _y
          cols_to_drop = [col for col in for_plot.columns if col.endswith('_y')]
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

          # create a column with the name feature if there is no one 

          for_plot = for_plot.rename(columns={feature_column: "feature"})

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
                  abbreviation=abbreviation
              )
          else:
              return ec_tile_categorical(
                  data=for_plot,
                  title=title,
                  title_position=title_position,
                  annotate_feature=annotate_feature,
                  abbreviation=abbreviation
              )


def ec_template(title, title_position, abbreviation):
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
    for_plot["text_color"] = define_annotation_color(for_plot["language_color"])

    # create a factor for correct coloring in ggplot 
    for_plot["language_color"] = pd.Categorical(
        for_plot["language_color"],
        categories=list(for_plot["language_color"]),
        ordered=True
    )

    # change labels to abbreviations 
    if abbreviation is True:
        for_plot["language"] = for_plot.apply(
            lambda r: r["language"] if pd.isna(r["abbreviation"]) else r["abbreviation"],
            axis=1
        )

    # create a map 
    map = (
        ggplot(for_plot, aes("x", "y"))
        + geom_tile(aes(fill="language_color"), show_legend=False)
        + geom_text(aes(label="language", color="text_color"), show_legend=False, size = 5.3)
        + theme_void()
        + scale_fill_manual(values=list(ec_languages["language_color"]))
        + scale_color_manual(values=["black", "white"])
        + labs(color=None, title=title)
        + theme(plot_title=element_text(hjust=title_position))
    )

    return map



def ec_tile_numeric(data, title, title_position, annotate_feature, abbreviation):
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

    # black for NA and grey90 for non-NA  
    for_plot["text_color"] = for_plot["feature"].isna().map(
        lambda is_na: "#000000" if is_na else "#E5E5E5"
    )

    #for_plot["alpha"] = for_plot["feature"].apply(lambda x: 0.85 if pd.isna(x) else 1)

    # subset with non-NA values
    for_plot_non_na = for_plot[for_plot["feature"].notna()].copy()

    # color mapping for correct order in the scale 
    color_mapping = {
        "#000000": "#000000",  # NA
        "#E5E5E5": "#E5E5E5"   # non-NA
    }

    # create a map 
    p = (
        ggplot(for_plot, aes("x", "y", alpha="alpha"))
        # base grey90 tiles
        + geom_tile(aes(alpha="alpha"), size=0, color="#E5E5E5", fill="#E5E5E5")
        # colored tiles only for non-NA
        + geom_tile(data=for_plot_non_na, mapping=aes(fill="feature", alpha="alpha"), size=0)
        + geom_text(aes(label="language", color="text_color"), size=5.3, show_legend=False)
        + theme_void()
        + labs(title=title) # removed legend title
        + theme(
            legend_position="bottom",
            plot_title=element_text(hjust=title_position, size=6.3),
            legend_text=element_text(size=5.3),
            legend_title=element_blank() # removed legend title
        )
        + guides(alpha="none", fill=guide_legend(title=None))
        + scale_color_manual(values=color_mapping)  
        + scale_fill_gradient(low="#DEEBF7", high="#2171B5") # some blue scale, lighter than ggplot default
    )

    return p



def ec_tile_categorical(data, title, title_position, annotate_feature, abbreviation):
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

    # black for both non-NA and NA 
    for_plot["text_color"] = for_plot["feature"].isna().map(
        lambda is_na: "#000000" if is_na else "#000000"
    )

    # subset with non-NA values 
    for_plot_non_na = for_plot[for_plot["feature"].notna()].copy()
    # convert to categorical
    for_plot_non_na["feature"] = pd.Categorical(for_plot_non_na["feature"])

    # color mapping for correct order in the scale 
    color_mapping = {
        "#000000": "#000000",  # non-NA
        "#999999": "#999999"  # NA
    }

    # create a map
    p = (
        ggplot(for_plot, aes("x", "y", alpha="alpha"))
        # base grey90 tiles
        + geom_tile(aes(alpha="alpha"), size=0, color="#E5E5E5", fill="#E5E5E5")
        # colored tiles only for non-NA
        + geom_tile(data=for_plot_non_na, mapping=aes(fill="feature"), size=0)
        + geom_text(aes(label="language", color="text_color"), size=5.3, show_legend=False)
        + theme_void()
        + labs(title=title)  # removed legend title

        + theme(
            legend_position="bottom",
            plot_title=element_text(hjust=title_position, size=6.3),
            legend_text=element_text(size=5.3),
            legend_title=element_blank()  # removed legend title
        )
        + guides(alpha="none", fill=guide_legend(title=None))  
        + scale_color_manual(values=color_mapping)
        + scale_fill_discrete(na_translate=False)
    )
    return p

