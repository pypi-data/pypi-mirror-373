from typing import TypedDict


class MetPalette(TypedDict):
    colors: tuple[str, ...]
    order: tuple[int, ...]
    colorblind: bool
