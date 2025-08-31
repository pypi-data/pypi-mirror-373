"""Grid overlay for matplotlib figures."""

import numpy as np

from . import locations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .classes import SciFigure

class GuideGridClass:
    """Handle the creation of a grid overlay for a figure.

    Grid overlay assist in positioning the elements of a figure.
    Note that the design of this class is tightly coupled with the SciFigure class
    (e.g. removal of axes and clear methods)
    """

    def __init__(
        self,
        figure: "SciFigure",
        major_interval: float = 5,
        minor_interval: float = 1,
        half_spacer: bool = True,
    ) -> None:
        """Create a grid overlay for a figure.

        :param figure: Figure to add the grid to
        :type figure: matplotlib.figure.Figure or scilayout.classes.SciFigure
        :param major_interval: Spacing of major grid, defaults to 5
        :type major_interval: int or float, optional
        :param minor_interval: Spacing of minor grid, defaults to 1
        :type minor_interval: int or float, optional
        :param half_spacer: Add half-spaced minor grid markers, defaults to True
        :type half_spacer: bool, optional
        """
        self.figure = figure
        self.major_interval = major_interval
        self.minor_interval = minor_interval
        self.half_spacer = half_spacer
        self.lines = {"x": {}, "y": {}}  # Store the lines for easy access
        self.line_kwargs = {"color": "k", "lw": 0.5, "alpha": 0.3}  # Default line
        self.major_scatter = None
        self.minor_scatter = None
        self.half_scatter = None
        self.ax = None

    def _create_axes(self) -> None:
        """Create an axes for the grid."""
        self.ax = self.figure.add_axes(
            [0, 0, 1, 1],  # Full figure size
            label="GuideGrid",
            frameon=False,
        )
        self.ax.set_navigate(False)

    def redraw(self) -> None:
        """Clear and draw the grid."""
        # TODO: check what happens after self.remove() is called

        if self.ax is None:
            self._create_axes()
        else:
            self.ax.clear()

        # Set limits to match the cm size of the figure
        width_cm, height_cm = locations.inch_to_cm(self.figure.get_size_inches())
        self.ax.set_ylim([height_cm, 0])
        self.ax.set_xlim([0, width_cm])

        # TODO: handle major, minor, and the half-minor markers
        #       Do I lock users in to 1cm grid or allow them to set the grid size?
        # Generate positions of each cm marker
        xlocs = np.arange(0, width_cm + 1, self.minor_interval)
        ylocs = np.arange(0, height_cm + 1, self.minor_interval)

        # Create 1cm mesh grid, make the 1cm markers and smaller 0.5 cm markers
        mesh = np.meshgrid(xlocs, ylocs)
        # Plot 1cm markers
        self.minor_scatter = self.ax.scatter(
            mesh[0], mesh[1], alpha=0.3, color="k", s=5, marker="+",
        )

        # Plot half_spacer
        if self.half_spacer:
            half_value = self.minor_interval / 2
            self.half_scatter = self.ax.scatter(
                mesh[0] + half_value,
                mesh[1] + half_value,
                marker="x",
                color="k",
                alpha=0.3,
                s=5,
                lw=0.3,
            )

        # Create 5cm mesh grid

        # mesh5 = np.meshgrid(xlocs[::5], ylocs[::5])
        xlocs = np.arange(0, width_cm + 1, self.major_interval)
        ylocs = np.arange(0, height_cm + 1, self.major_interval)
        meshmajor = np.meshgrid(xlocs, ylocs)
        self.major_scatter = self.ax.scatter(
            meshmajor[0], meshmajor[1], color="k", marker="+", lw=2, alpha=0.3
        )

        # Draw user defines guidelines
        for axis in ["x", "y"]:
            for location in self.lines[axis]:
                if axis == "x":
                    self.ax.axvline(location, **self.lines[axis][location])
                else:
                    self.ax.axhline(location, **self.lines[axis][location])

    def add_line(self, axis: str, location: float) -> None:
        """Add a line to the grid.

        Useful for adding specific guidelines to the grid.
        Line appearance can be modified with GuideGridClass.lines[axis][location], where
        the value is a dict containing the kwargs for axhline or axvline that's used to
        draw the line.

        clear_lines() to remove all lines.

        :param axis: Axis to add the line to, 'x' or 'y'
        :type axis: str
        :param location: Location of the line
        :type location: float or int
        """
        if axis not in ["x", "y"]:
            msg = "Axis must be either 'x' or 'y'"
            raise ValueError(msg)
        self.lines[axis][location] = self.line_kwargs
        self.redraw()

    def clear_lines(self) -> None:
        """Remove all user specified lines from the grid."""
        self.lines = {"x": {}, "y": {}}
        self.redraw()

    def detach_ax(self) -> None:
        """Detach the grid from the axes."""
        if self.ax:
            self.ax.clear()
            self.ax = None

    def remove(self) -> None:
        """Clean up resources."""
        if self.major_scatter:
            self.major_scatter.remove()
        if self.half_scatter:
            self.half_scatter.remove()
        self.detach_ax()

    def hide(self) -> None:
        """Hide the grid."""
        self.ax.set_visible(False)
        self.figure.canvas.draw()

    def show(self) -> None:
        """Show the grid."""
        if self.ax is None:
            self.redraw()
        self.ax.set_visible(True)
        self.figure.canvas.draw()
