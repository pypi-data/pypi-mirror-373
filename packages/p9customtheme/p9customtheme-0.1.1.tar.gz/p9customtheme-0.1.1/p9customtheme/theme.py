import matplotlib.font_manager as fm
from plotnine import (
    element_blank,
    element_line,
    element_text,
    theme,
    theme_bw,
)

from .settings import (
    DEFAULT_DPI,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
)


def _check_if_font_exists(font: str, verbose: bool = False) -> bool:
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    found = font in available_fonts
    if verbose:
        if not found:
            print(f"Font '{font}' NOT found")
    return found


class custom_theme(theme_bw):
    def __init__(
        self,
        base_size: int | float = 12,
        base_family: str | list[str] = ["Roboto", "sans-serif"],
        rotate_label: int = 0,
        legend_position: str = "outside",
        verbose: bool = False,
    ):
        # for all fonts check if they are available
        if isinstance(base_family, str):
            base_family = [base_family]
        base_family = [
            f for f in base_family if _check_if_font_exists(f, verbose=verbose)
        ]
        if len(base_family) == 0:
            base_family = ["sans-serif"]
        super().__init__(int(base_size), base_family)

        self += theme(
            panel_grid=element_blank(),  # Remove any grid lines
            panel_border=element_blank(),  # Remove the border around the plot
            axis_line_x=element_line(color="black"),
            axis_line_y=element_line(color="black"),
            axis_text=element_text(linespacing=1.2, color="black", size=base_size),
            axis_ticks_pad_major_x=3,
            axis_ticks_pad_major_y=1,
            axis_ticks_length=7,
            axis_title=element_text(size=base_size * 1.1),
            legend_key_size=base_size + 1,
            legend_key=element_blank(),
            legend_text=element_text(size=base_size, margin={"l": 5}),
            plot_margin=0.005,
            figure_size=(DEFAULT_WIDTH, DEFAULT_HEIGHT),
            dpi=DEFAULT_DPI,
            plot_title=element_text(size=base_size * 1.2, ha="left"),
            plot_subtitle=element_text(size=base_size, ha="left"),
            svg_usefonts=False,
            strip_background=element_blank(),
            strip_text=element_text(color="black", size=base_size * 0.8),
        )
        if rotate_label > 0:
            self += theme(axis_text_x=element_text(rotation=rotate_label))

        if legend_position == "inside":
            self += theme(
                legend_position="inside",
                legend_position_inside=(1, 1),  # Set to (0,1) for top left)
            )
