import pandas as pd
import plotnine as p9
import polars as pl
from plotnine.data import mtcars, penguins

from p9customtheme import custom_discrete, custom_theme
from p9customtheme.utils import to_pandas_categories


def test_simple_plot():
    p = p9.ggplot(mtcars, p9.aes("wt", "mpg")) + p9.geom_point()
    if p != "test_simple_plot":
        p.save("tests/baseline/test_simple_plot_fail.png", verbose=False)
    assert p == "test_simple_plot"


def test_boxplot():
    p = (
        p9.ggplot(penguins, p9.aes("species", "bill_length_mm", fill="island"))
        + p9.geom_boxplot()
        + custom_discrete()
        + p9.labs(
            title="Penguin bill length by species and island".title(),
            subtitle="A comparison based on example data",
            x="species",
            y="bill length [mm]",
            fill="Island",
        )
    )
    if p != "boxplot_simple":
        p.save("tests/baseline/boxplot_simple_fail.png", verbose=False)

    assert p == "boxplot_simple"


def test_colors():
    colors_n = 7
    df = pl.DataFrame(
        {"y": list(range(1, colors_n + 1)), "x": [f"{i}" for i in range(colors_n)]}
    )
    p = (
        p9.ggplot(df, p9.aes("x", "y", fill="x"))
        + p9.geom_col()
        + custom_discrete()
        + p9.scale_y_continuous(expand=(0, 0))
    )
    if p != f"colors_{colors_n}":
        p.save(f"tests/baseline/colors_{colors_n}_fail.png", verbose=False)
    assert p == f"colors_{colors_n}"


def test_scatter_colors():
    p = (
        p9.ggplot(penguins, p9.aes("bill_depth_mm", "bill_length_mm", fill="species"))
        + p9.geom_point()
        + p9.labs(
            title="Penguin Bill Length vs Depth",
            x="Bill Depth [mm]",
            y="Bill Length [mm]",
            fill="Species",
        )
        + custom_discrete()
    )
    if p != "scatter_colors":
        p.save("tests/baseline/scatter_colors_fail.png", verbose=False)
    assert p == "scatter_colors"


def test_grid():
    p = (
        p9.ggplot(penguins, p9.aes("bill_depth_mm", "bill_length_mm", fill="sex"))
        + p9.geom_point()
        + p9.labs(
            title="Penguin Bill Length vs Depth",
            x="Bill Depth [mm]",
            y="Bill Length [mm]",
            fill="Sex",
        )
        + p9.facet_grid("species ~ island")
        + custom_discrete()
        + p9.theme(panel_border=p9.element_rect(color="black"))
        + custom_theme(base_size=9.5)
    )
    if p != "grid_plot":
        p.save("tests/baseline/grid_plot_fail.png", verbose=False)
    assert p == "grid_plot"


def test_complex_grid():
    p = (
        p9.ggplot(
            to_pandas_categories(
                pl.DataFrame(penguins.dropna())
                .with_columns(pl.col("body_mass_g") / 1000)
                .group_by(["species", "year", "sex"])
                .agg(pl.col("body_mass_g").mean())
                .with_columns(pl.col("year").cast(pl.String))
            ),
            mapping=p9.aes(x="year", y="sex", size="body_mass_g", fill="species"),
        )
        + p9.geom_point()
        + p9.facet_wrap("~species", ncol=1)
        + p9.labs(
            title="Penguin Mean Weight",
            x="Year",
            y="Sex",
            size="Body Mass [kg]",
            fill="Species",
        )
        + custom_theme(rotate_label=90)
        + p9.theme(
            figure_size=(5, 6),
            plot_title=p9.element_text(ha="center"),
        )
        + custom_discrete(reverse=True)
    )
    if p != "grid_complex_plot":
        p.save("tests/baseline/grid_complex_plot_fail.png", verbose=False)
    assert p == "grid_complex_plot"


def test_to_pandas_categories():
    df = (
        pl.DataFrame(penguins.dropna())
        .with_columns(pl.col("body_mass_g") / 1000)
        .group_by(["species", "year", "sex"])
        .agg(pl.col("body_mass_g").mean())
        .with_columns(pl.col("year").cast(pl.String))
    )
    pdf = to_pandas_categories(df)
    assert isinstance(pdf, pd.DataFrame)

    assert pdf["species"].dtype.name == "category"
    assert len(pdf["species"].cat.categories) == 3
