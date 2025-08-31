from typing import TYPE_CHECKING

from planar.dependencies import lazy_exports

lazy_exports(
    __name__,
    {
        "PlanarDataset": (".dataset", "PlanarDataset"),
    },
)

if TYPE_CHECKING:
    from .dataset import PlanarDataset

    __all__ = [
        "PlanarDataset",
    ]
