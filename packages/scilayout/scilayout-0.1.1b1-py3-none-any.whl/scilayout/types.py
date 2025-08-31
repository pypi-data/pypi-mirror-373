"""Type definitions for scilayout."""

from dataclasses import dataclass
from typing import NamedTuple

centimetres = float
"""A type alias for centimeters, used for positions and dimensions in figures."""
inches = float
"""A type alias for inches, used for positions and dimensions in figures."""
fraction = float
"""A type alias for figure fraction, used for positions and dimensions in figures."""

@dataclass
class Extent(NamedTuple):
    """A named tuple to hold extent (position) coordinates."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        """Ensure that the coordinates are in the correct order."""
        if not all(isinstance(coord, (int, float)) for coord in (self.x0, self.y0, self.x1, self.y1)):
            msg = "Coordinates must be numeric (int or float)."
            raise TypeError(msg)

        if self.x0 > self.x1 or self.y0 > self.y1:
            msg = "Coordinates must be in the order: (x0, y0, x1, y1)."
            raise ValueError(msg)

class Bound(NamedTuple):
    """A named tuple to hold bounding box (width, height) coordinates."""

    x: float
    y: float
    w: float
    h: float


class ExtentCM(Extent):
    """A named tuple to hold extent (position) coordinates."""

    x0: centimetres
    y0: centimetres
    x1: centimetres
    y1: centimetres


class BoundCM(Bound):
    """A named tuple to hold bounding box (width, height) coordinates."""

    x: centimetres
    y: centimetres
    w: centimetres
    h: centimetres


class ExtentInches(Extent):
    """A named tuple to hold extent (position) coordinates in inches."""

    x0: inches
    y0: inches
    x1: inches
    y1: inches


class BoundInches(Bound):
    """A named tuple to hold bounding box (width, height) coordinates in inches."""

    x: inches
    y: inches
    w: inches
    h: inches


class ExtentFraction(Extent):
    """A named tuple to hold extent (position) coordinates in figure fraction."""

    x0: fraction
    y0: fraction
    x1: fraction
    y1: fraction
