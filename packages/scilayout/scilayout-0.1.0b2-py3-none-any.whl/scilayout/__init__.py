"""scilayout package.

This package provides tools for creating and managing scientific figures with a focus on
layout in centimeters and an upper-left origin. It includes classes for figures, axes,
text, and scalebars.
"""

__version__ = "0.1.0b2"
__all__ = ["__version__"]
# Import dependencies
import matplotlib.pyplot as plt

# Import sub-modules
from . import (
    base,
    classes,
    locations,
    scalebars,
    stats,
    style,
)

# TODO: add sub-modules to __all__ to finalise API
# __all__ += [
#     "base",
#     "classes",
#     "locations",
#     "scalebars",
#     "stats",
#     "style",
# ]


def figure(**kwargs) -> classes.SciFigure:
    """Create a SciFigure object.

    This function is wraps plt.figure()
    Please see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
    for documentation about figure arguments and keyword arguments.

    Example usage:

    ```python
    %matplotlib
    import scilayout
    fig = scilayout.figure()
    ax_1 = fig.add_panel((1, 2, 4, 5))
    ax_1
    ```
    :param name: Name of the figure
    :type name: str, optional
    :return: SciFigure object (the plot window)
    :rtype: scilayout.figures.SciFigure
    """
    if "FigureClass" in kwargs:
        msg = "Cannot set FigureClass in scilayout.figure(), use scilayout.classes.SciFigure instead."
        raise ValueError(msg)
    return plt.figure(FigureClass=classes.SciFigure, **kwargs)
