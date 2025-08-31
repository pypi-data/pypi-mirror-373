"""Movable scalebars for matplotlib plots."""

import numpy as np

from . import style


class ScaleBar:
    """Scale bar for matplotlib plots
    Both horizontal and vertical scale bars.
    A scalebar that can be respositioned using the move() method.
    """

    def __init__(
        self,
        ax,
        xy,
        length,
        unit=None,
        coordSystem="fraction",
        orientation="h",
        hpos=None,
        vpos=None,
        transform="transData",
        textstring=None,
        lw=None,
        fontsize=None,
    ):
        """Create a scalebar on a matplotlib axes

        :param ax: Axes to draw the scalebar on
        :type ax: matplotlib.axes.Axes
        :param length: Length of the scalebar
        :type length: float or int
        :param xy: Position of the scalebar in data coordinates
        :type xy: tuple
        :param unit: Unit of the scalebar, optional
        :type unit: str
        :param orientation: Orientation of the scalebar. 'h' for horizontal (default), 'v' for vertical
        :type orientation: str, optional
        :param coordSystem: Units of the xy position. 'fraction' (default), 'data' or 'cm'
        :type coordSystem: str, optional
        :param hpos: Horizontal position of the text. Behaviour depends on orientation
        :type hpos: str
        :param vpos: Vertical position of the text. Behaviour depends on orientation
        :type vpos: str
        :param textstring: Text to display on the scalebar. Defaults to the length and unit
        :type textstring: str
        :param lw: Linewidth of the scalebar, default 1
        :type lw: float
        :param fontsize: Font size of the text, default 8
        :type fontsize: int
        """
        # Sort out orientations
        orientation = "h" if orientation in ["horizontal", "h"] else "v"
        assert orientation in ["h", "v"], "orientation must be 'h' or 'v'"
        if orientation == "h":
            if vpos is None:
                vpos = "bottom"
            assert vpos in ["top", "bottom"], "Unknown vertical alignment"
        else:
            if hpos is None:
                hpos = "left"
            assert hpos in ["left", "right"], "Unknown horizontal alignment"
        vpos = vpos if vpos is not None else "center"
        hpos = hpos if hpos is not None else "center"

        assert coordSystem in ["fraction", "data", "cm"], "Unknown units"
        assert transform in ["transAxes", "transData"], "Unknown transform"
        if transform == "transAxes":
            raise NotImplementedError("transAxes not yet implemented")

        self.ax = ax
        self.xypos = xy
        self.coordSystem = coordSystem
        self._transform = transform  # for now this cannot be changed after creation
        self.orientation = orientation
        self.length = length
        self.line = None

        # Text items
        self.text = None
        self.unit = unit
        self.textstring = textstring
        self.hpos = hpos
        self.vpos = vpos
        self.lw = 1 if lw is None else lw
        self.fontsize = (
            style.params["scalebars.fontsize"] if fontsize is None else fontsize
        )

        self.text_pixel_pad_proportion = 0.5
        # self.test_line_pad_cm = 0.025  # TODO: express padding as cm

        self._initialise_scalebar(*xy)

    def _initialise_scalebar(self, x, y):
        """Initialise the scalebar and text objects"""
        if self.orientation == "h":
            if self.vpos == "top":
                va = "bottom"
            elif self.vpos == "bottom":
                va = "top"
            else:
                va = "center"
            text_kwargs = dict(ha=self.hpos, va=va)
        else:
            if self.hpos == "left":
                ha = "right"
            elif self.hpos == "right":
                ha = "left"
            else:
                ha = "center"
            text_kwargs = dict(rotation=90, ha=ha, va=self.vpos)

        text_xpos, text_ypos = 0, 0
        x_locs, y_locs = [0, 1], [0, 1]
        transform = (
            self.ax.transAxes if self._transform == "transAxes" else self.ax.transData
        )
        self.line = self.ax.plot(
            x_locs,
            y_locs,
            "k",
            lw=self.lw,
            transform=transform,
            clip_on=False,
        )[0]
        textstring = (
            f"{self.length} {self.unit}" if self.textstring is None else self.textstring
        )
        self.text = self.ax.text(
            text_xpos,
            text_ypos,
            textstring,
            transform=transform,
            size=self.fontsize,
            **text_kwargs,
        )
        self.move(x, y)

    def move(self, x, y, coordSystem=None):
        """Move the scalebar to a new position

        :param x: x-coordinate of the new position
        :type x: float
        :param y: y-coordinate of the new position
        :type y: float
        :param coordSystem: scale type of the new position. Defaults to object's unit type
        :type coordSystem: str, optional
        """
        coordSystem = self.coordSystem if coordSystem is None else coordSystem
        assert coordSystem in ["fraction", "data", "cm"], "Unknown units"

        self._update_appearance()

        x_locs, y_locs = self._find_x_y(x, y, coordSystem)

        # Calculate text width in display coordinates
        renderer = self.ax.get_figure().canvas.get_renderer()
        text_bbox = self.text.get_window_extent(renderer)
        inv_transform = self.ax.transData.inverted()
        text_width_data = (
            inv_transform.transform((text_bbox.width, 0))[0]
            - inv_transform.transform((0, 0))[0]
        )
        text_height_data = (
            inv_transform.transform((0, text_bbox.height))[1]
            - inv_transform.transform((0, 0))[1]
        )

        # Find line bbox
        line_bbox = self.line.get_window_extent(renderer)
        # TODO: make the line width change the padding

        # Convert text width to data coordinates
        inv_transform = self.ax.transData.inverted()
        if self.orientation == "h":
            text_xpos, text_ypos = np.mean(x_locs), y_locs[0]
            if self.vpos == "top":
                text_ypos = (
                    text_ypos + text_height_data * self.text_pixel_pad_proportion
                )
            elif self.vpos == "bottom":
                text_ypos = (
                    text_ypos - text_height_data * self.text_pixel_pad_proportion
                )
            elif self.vpos == "center":
                pass
            else:
                raise ValueError(f"Unknown vertical alignment: {self.vpos}")
        elif self.orientation == "v":
            text_xpos, text_ypos = x_locs[0], np.mean(y_locs)
            if self.hpos == "left":
                text_xpos = text_xpos - text_width_data * self.text_pixel_pad_proportion
            elif self.hpos == "right":
                text_xpos = text_xpos + text_width_data * self.text_pixel_pad_proportion
            else:
                raise ValueError(f"Unknown horizontal alignment: {self.hpos}")
        else:
            raise ValueError(f"Unknown orientation: {self.orientation}")

        self.text.set_position((text_xpos, text_ypos))
        self.line.set_xdata(x_locs)
        self.line.set_ydata(y_locs)

        self.ax.figure.canvas.draw()  # to update the display of the modified objects

    def _find_x_y(self, x, y, coordSystem):
        """Find the x and y coordinates of the scalebar

        :param x: x-coordinate of the new position
        :type x: float
        :param y: y-coordinate of the new position
        :type y: float
        :param coordSystem: scale type of the new position ('fraction', 'data', 'cm')
        :type coordSystem: str
        :return: Coordinates of the scalebar in data coordinates
        :rtype: Tuple(List[float, float], List[float, float])
        """
        if coordSystem == "fraction":
            x, y = self.ax.transAxes.transform((x, y))
            x, y = self.ax.transData.inverted().transform((x, y))
            print(f"Fractional coordinates: {x}, {y}")
        elif coordSystem == "cm":
            x0, y0, x1, y1 = (
                self.ax.get_location()
            )  # position in cm from top left of figure
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            xscale = (x1 - x0) / (xlim[1] - xlim[0])
            yscale = (y1 - y0) / (ylim[1] - ylim[0])
            x = xlim[0] + (x - x0) / xscale
            y = ylim[1] - (y - y0) / yscale  # y is inverted
        elif coordSystem == "data":
            pass
        else:
            raise ValueError(f"Unknown coordinate system: {coordSystem}")

        if self.orientation == "h":
            x_locs = [x, x + self.length]
            y_locs = [y, y]
        else:
            x_locs = [x, x]
            y_locs = [y, y + self.length]
        return x_locs, y_locs

    def _update_appearance(self):
        """Update the appearance of the scalebar"""
        self.text.set_size(self.fontsize)
        self.line.set_linewidth(self.lw)
        self.ax.figure.canvas.draw()


class LinkedScaleBar:
    def __init__(
        self,
        ax,
        xy,
        x_length,
        y_length,
        x_unit=None,
        y_unit=None,
        coordSystem="fraction",
        hat=None,
        vat=None,
        transform="transData",
        x_textstring=None,
        y_textstring=None,
        lw=None,
    ):
        if vat is None:
            vat = "bottom"
        self.x_scalebar = ScaleBar(
            ax,
            xy,
            x_length,
            x_unit,
            coordSystem,
            orientation="h",
            vpos=vat,
            transform=transform,
            textstring=x_textstring,
            lw=lw,
        )
        self.y_scalebar = ScaleBar(
            ax,
            xy,
            y_length,
            y_unit,
            coordSystem,
            orientation="v",
            hpos=hat,
            transform=transform,
            textstring=y_textstring,
            lw=lw,
        )
        self.ax = ax

    def move(self, x, y, coordSystem=None):
        self.x_scalebar.move(x, y, coordSystem)
        self.y_scalebar.move(x, y, coordSystem)
