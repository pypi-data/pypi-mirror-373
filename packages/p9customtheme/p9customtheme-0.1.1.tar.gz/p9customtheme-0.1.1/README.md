# p9customtheme

My personal plotnine theme package.
You can use it but changes to the theme will appear with minimal versioning.

If you want a reproducible experience make sure to pin the version in your dependency.

[Plotnine](https://github.com/has2k1/plotnine) is awesome and a big thanks to the developers for making it.

## Installation

Install this theme using `pip` ur `uv`:

```bash
uv pip install p9customtheme
```

## Usage

You can simply install the package. Once you import it the theme is set as the default:

```python
import p9customtheme
```

That is all you need.

Here is a more complete example showing also the color scale option:

```python
from p9customtheme import custom_discrete, custom_theme
import plotnine as p9
from plotnine.data import penguins

(
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
```

![A boxplot with the custom theme](./tests/baseline/boxplot_simple.png "Penguin Boxplot")

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

```bash
cd p9customtheme
uv venv
source ./venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
uv pip install -e '.[test]'
```

Before any PR ensure the tests as passing with:

```bash
pytest .
```
