# PyCaucTile
A package that generates tile grid maps for illustrating features of East Caucasian languages. The plots are created using `plotnine` library, providing a ggplot2-like interface in Python. 
There is an R package that shares the same functionality (see [`RCaucTile`](https://github.com/LingConLab/RCaucTile)) by George Moroz.


## Installation
```bash
pip install pycauctile
```

## Example usage
```python
from pycauctile import ec_tile_map, ec_languages

map = ec_tile_map()
map
```
![example image](examples/figures/example1.png)

```python
map = ec_tile_map(ec_languages,
            feature_column = "consonant_inventory_size",
            title = "Consonant inventory size (Moroz 2021)",
            annotate_feature = True)
map
```
![example image](examples/figures/example2.png)

## Citation