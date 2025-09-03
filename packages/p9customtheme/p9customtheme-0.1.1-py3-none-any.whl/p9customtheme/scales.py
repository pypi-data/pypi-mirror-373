import logging
import random

from plotnine.scales import scale_fill_manual

from .colors import MET_PALETTES
from .logging import logger
from .types import MetPalette


class custom_discrete(scale_fill_manual):
    def __init__(
        self,
        name: str = "Hiroshige",
        order: str = "discrete",
        reverse: bool = False,
        colorblind: bool = True,
        **kwargs,
    ):
        """Create a custom discrete color scale based on Met Museum palettes.

        Args:
            name (str, optional): Name of the color palette to use. Defaults to "Hiroshige".
            order (str, optional): Order of colors to use from palette ('discrete' or 'gradient'). Defaults to "discrete".
            reverse (bool, optional): Whether to reverse the color order. Defaults to False.
            colorblind (bool, optional): Whether to use colorblind-friendly palette. Defaults to True.

        Raises:
            ValueError: If the specified palette name doesn't exist
            ValueError: If the order parameter is not one of 'discrete' or 'gradient'
        """
        name = name.lower()
        if name not in MET_PALETTES and name != "random":
            raise ValueError(f"Unknown palette '{name}'")

        if name == "random":
            if colorblind:
                options = [k for k, v in MET_PALETTES.items() if v["colorblind"]]
            else:
                options = list(MET_PALETTES.keys())
            name = random.choice(options)
            msg = f"Using random palette '{name}' ({'colorblind safe' if MET_PALETTES[name]['colorblind'] else 'not colorblind safe'})"
            logger.info(msg)

        self.colorpalette: MetPalette = MET_PALETTES[name]
        self.name = name
        self.reverse = reverse
        if order not in ("discrete", "continuous"):
            raise ValueError(
                f"Unknown ordering {order}, must be 'discrete' or 'continuous'"
            )
        self._ordering = order
        # Bit of a hack to do a list of the key here
        super().__init__([name], **kwargs)

    def __post_init__(self, palette_name: list[str]):
        self.colorpalette = MET_PALETTES[palette_name[0]]
        super().__post_init__(self.colorpalette["colors"])

        def palette(n):
            max_n = len(self.colorpalette["colors"])
            if n > max_n:
                msg = (
                    f"The palette of {self.__class__.__name__} ({self.name}) can return "
                    f"a maximum of {max_n} values. {n} were requested "
                    f"from it."
                )
                raise ValueError(msg)
            # else we return values in order for discrete values
            values = []
            if self._ordering.startswith("d"):
                for index in self.colorpalette["order"][:n]:
                    values.append(self.colorpalette["colors"][index - 1])
            else:
                values = self.colorpalette["colors"][:n]
            if self.reverse:
                values = values[::-1]
            return values

        self.palette = palette
