from plotnine import (
    geoms,
    theme_set,
)
from plotnine.options import set_option

from .colors import _all_colors as show_all_colors  # noqa: F401
from .scales import custom_discrete  # noqa: F401
from .settings import (
    DARK_GRAY,
    DEFAULT_DPI,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    LIGHT_GRAY,
)
from .theme import custom_theme

geoms.geom_point.DEFAULT_AES["shape"] = "o"
geoms.geom_point.DEFAULT_AES["size"] = 2
geoms.geom_point.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_point.DEFAULT_AES["fill"] = LIGHT_GRAY


geoms.geom_col.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_bar.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_boxplot.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_tile.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_histogram.DEFAULT_AES["color"] = DARK_GRAY
geoms.geom_histogram.DEFAULT_AES["fill"] = LIGHT_GRAY

theme_set(custom_theme())
set_option("dpi", DEFAULT_DPI)
set_option("figure_size", (DEFAULT_WIDTH, DEFAULT_HEIGHT))
set_option("figure_format", "svg")


__all__ = (
    "custom_theme",
    "custom_discrete",
    "show_all_colors",
)
