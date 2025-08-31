"""Helper functions and classes for plotting stats information on an axes."""

from matplotlib import transforms


class StatsLine:
    def __init__(self, ax, y, x0, x1):
        """Horizontal statistical line with vertical line at the end.

        :param ax: Axes to draw the line
        :type ax: matplotlib.axes.Axes
        :param y: y location of the line in axis proportion
        :type y: float
        :param x0: x location of the start of the line in data coordinates
        :type x0: float
        :param x1: x location of the end of the line in data coordinates
        :type x1: float
        """
        self.ax = ax
        self.y = y
        self.x0 = x0
        self.x1 = x1
        self.main_bar = None
        self.right_drop = None
        self.left_drop = None
        self.linewidth = 1
        self.color = "black"
        self.drop_amount = 0.025
        self.transform = transforms.blended_transform_factory(ax.transData, ax.transAxes)
        self.draw()

    def draw(self) -> None:
        """Draw/redraw the line on the axis."""
        # remove existing lines
        for line in [self.main_bar, self.left_drop, self.right_drop]:
            if line is not None:
                line[0].remove()

        # Save current axis limits (.plot() may alter them)
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # TODO: implement style support here
        # turn off clip
        stylekwargs = dict(color=self.color,
                           linewidth=self.linewidth,
                           transform=self.transform,
                           clip_on=False,
                           label="_nolegend_")

        self.main_bar = self.ax.plot([self.x0, self.x1], [self.y, self.y], **stylekwargs)
        self.left_drop = self.ax.plot([self.x0, self.x0], [self.y, self.y - self.drop_amount], **stylekwargs)
        self.right_drop = self.ax.plot([self.x1, self.x1], [self.y, self.y - self.drop_amount], **stylekwargs)

        # Restore the xy limits
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def set_transform(self, x="data", y="axes"):
        """Set the transform for the stat bar

        Transform type can be 'data' or 'axes'.
        - 'data' will set the transform to the data coordinates of the axis.
        - 'axes' will set the transform to the proportion of the axis. Resizing the axis will not affect the position of the line

        :param x: x transform type
        :type x: str
        :param y: y transform type
        :type y: str
        """
        transform = dict(x=None, y=None)
        for key, val in zip(["x", "y"], [x, y]):
            if val == "data":
                transform[key] = self.ax.transData
            elif val == "axes":
                transform[key] = self.ax.transAxes
            else:
                raise ValueError(f"Unknown transform type {val}")
        self.transform = transforms.blended_transform_factory(transform["x"], transform["y"])
        self.draw()
