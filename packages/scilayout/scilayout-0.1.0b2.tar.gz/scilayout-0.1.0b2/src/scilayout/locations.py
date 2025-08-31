"""Convert between cm, inch, and fraction locations in matplotlib figures."""

from __future__ import annotations

import matplotlib.figure
import numpy as np
from matplotlib.transforms import Transform

from .types import BoundCM, ExtentCM, ExtentInches, centimetres, inches


def locationcm_to_position(
    fig: matplotlib.figure.Figure,
    location_corners: ExtentCM
    | tuple[centimetres, centimetres, centimetres, centimetres],
) -> ExtentInches:
    """Convert an upper left origin cm extent to figure fraction rect.

    :param fig: Figure window to find true size from
    :type fig: matplotlib.figure.Figure
    :param location_corners: (x1, y1, x2, y2), origin point is upper left of figure (y1 is visual up), cm units
    :type location_corners: ExtentCM (Tuple[float, float, float, float])
    :return: (x1, y1, width, height), origin point is lower left of figure (y1 is visual down), fraction units
    :rtype: ExtentInches (Tuple[float, float, float, float])
    """
    x0_cm, y0_cm, x1_cm, y1_cm = location_corners
    if x0_cm > x1_cm or y0_cm > y1_cm:
        msg = "x0 must be less than x1 and y0 must be less than y1"
        raise ValueError(msg)

    # Create the transform for centimeter-based positioning
    cm_transform = CMTransform(fig)

    # Transform the (x0_cm, y0_cm) and (x1_cm, y1_cm) positions
    transformed_coords = cm_transform.transform([[x0_cm, y0_cm], [x1_cm, y1_cm]])

    # Extract transformed figure coordinates
    left, top = transformed_coords[0]  # Top-left corner in figure coordinates
    right, bottom = transformed_coords[1]  # Bottom-right corner in figure coordinates

    # Calculate width and height in figure coordinates
    width_figure = right - left
    height_figure = top - bottom

    # Convert into position
    return (left, bottom, width_figure, height_figure)


# TODO: check precision conversions of integer
# setting to location .5 and back again gives a slight difference
def cm_to_inch(cm: centimetres) -> inches:
    """Convert centimeters to inches."""
    return cm / 2.54


def inch_to_cm(inch: inches) -> centimetres:
    """Convert inches to centimeters."""
    return inch * 2.54


def cm_to_fraction(fig, xy):
    """Convert upper left cm to standard axes fraction.

    :param fig:
    :type fig: matplotlib.figures.Figure
    :param xy: (x, y) origin upper left
    :type xy: Tuple[float, float]
    :return: xfrac, yfrac, origin lower left
    :rtype: Tuple[float, float]
    """
    figsize = inch_to_cm(fig.get_size_inches())
    width = xy[0]
    height = figsize[1] - xy[1]
    return width / figsize[0], height / figsize[1]


def fraction_to_cm(fig, xy) -> tuple[centimetres, centimetres]:
    """Convert standard axes fraction to upper left cm.

    :param fig:
    :type fig: matplotlib.figures.Figure
    :param xy: (x, y) axes fraction origin lower left
    :type xy: Tuple[float, float]
    :return: (x, y) cm origin upper left
    :rtype: Tuple[float, float]
    """
    figsize = inch_to_cm(fig.get_size_inches())
    return xy[0] * figsize[0], figsize[1] - (figsize[1] * xy[1])


# --- Classes ---
class CMTransform(Transform):
    """A transformation class to convert coordinates from centimeters to figure
    fractions in a Matplotlib figure."""

    input_dims = 2
    output_dims = 2
    has_inverse = True

    def __init__(self, fig: matplotlib.figure.Figure) -> None:
        """Initialize the CMTransform.

        :param fig: The figure to calculate the transform on.
        :type fig: matplotlib.figure.Figure
        """
        super().__init__()
        self.fig = fig

    def transform(self, values):
        inch_coords = np.array(values) / 2.54
        figwidth, figheight = self.fig.get_size_inches()
        x, y = inch_coords.T
        return np.array([x / figwidth, 1 - (y / figheight)]).T  # flip y

    def inverted(self):
        return InvertedCMTransform(self.fig)


class InvertedCMTransform(Transform):
    input_dims = 2
    output_dims = 2
    has_inverse = True

    def __init__(self, fig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig = fig

    def transform(self, values):
        # Convert figure coordinates to inches
        figwidth, figheight = self.fig.get_size_inches()
        x, y = np.array(values).T
        inch_coords = np.array(
            [x * figwidth, (1 - y) * figheight],
        ).T  # Flip y-axis back

        # Convert inches to cm
        return inch_coords * 2.54

    def inverted(self):
        return CMTransform(self.fig)
