"""Base plotting functions for use in scientific plotting."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from . import locations, style
from .types import centimetres, inches


def create_panel_label(
    ax: mpl.axes.Axes,
    text: str,
) -> mpl.text.Text:
    """Add a panel label in figure fraction coordinates.

    :param ax: Axes object to attach the label to
    :type ax: matplotlib.axes.Axes
    :param text: The text to add to a panel
    :type text: str
    :return: An axes text object
    :rtype: matplotlib.text.Text
    """
    # Get the position of axes top left corner in figure coordinates
    bbox = ax.get_position().bounds
    x = bbox[0]
    y = bbox[1] + bbox[3]  # the position here is in ypos + width

    # Handle the case of the text
    panel_label_case = style.params["panellabel.case"]
    if panel_label_case is None:
        # Display the label as it was written at initialisation
        pass
    elif panel_label_case == "upper":
        text = text.upper()
    elif panel_label_case == "lower":
        text = text.lower()

    return ax.text(
        x,
        y,
        text,
        fontfamily=style.params["panellabel.font"],
        fontweight=style.params["panellabel.fontweight"],
        size=style.params["panellabel.fontsize"],
        label="_nolegend_",  # Don't include in legend
        transform=ax.get_figure().transFigure,
    )


# TODO: determine if this is required
def create_panel_locations(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    npanels: tuple[int, int],
    pad: float = 0.5,
) -> np.ndarray:
    """Find locations of panels.

    :param x1: Left x location
    :type x1: float
    :param y1: Top y location
    :type y1: float
    :param x2: Right x location
    :type x2: float
    :param y2: Bottom y location
    :type y2: float
    :param npanels: Number of divisions
    :type npanels: Tuple[int, int]
    :param pad: padding between each
    :type pad: float
    :return: Array containing coordinates for each panel
    :rtype: numpy.typing.ndarray
    """
    # Ruff doesn't like assert
    if not (npanels[0] > 0 and npanels[1] > 0):
        msg = "panels must be positive integers"
        raise ValueError(msg)

    # initialise numpy array object
    panel_array = np.zeros((*npanels, 4), dtype=float)

    height = (y2 - y1 - (npanels[0] - 1) * pad) / npanels[0]
    width = (x2 - x1 - (npanels[1] - 1) * pad) / npanels[1]
    for idx in range(npanels[0]):
        for jdx in range(npanels[1]):
            location = (
                x1 + jdx * (width + pad),
                y1 + idx * (height + pad),
                x1 + jdx * (width + pad) + width,
                y1 + idx * (height + pad) + height,
            )
            panel_array[idx, jdx] = location

    return panel_array


def savefigure(
    fig: mpl.figure.Figure,
    fpath: Path,
    dpi: float = 300.0,
    transparent_png: bool = True,
    bbox: str = "tight",
    allow_overwrite: bool = True,
) -> None:
    """Save figure using settings optimised for version control and document embedding.

    The default 'tight' bounding box will crop the whitespace around the figure.

    :param fig: Figure to save
    :type fig: matplotlib.figures.Figure
    :param fpath: Path to save the figure to
    :type fpath: pathlib.Path or str
    :param dpi: Dots per inch, default 300
    :type dpi: float or int
    :param transparent_png: Make png output transparent
    :type transparent_png: bool
    :param bbox: Bounding box to use for pdf and eps output, default 'tight'
    :type bbox: str
    """
    if not isinstance(fpath, Path):
        fpath = Path(fpath)
    if fpath.exists():
        if allow_overwrite:
            print(f"Overwriting {fpath}")  # TODO: use logging to display messages
        else:
            msg = f"{fpath} already exists, set allow_overwrite=True to overwrite"
            raise FileExistsError(msg)
    fig_fmt = fpath.suffix

    common_kwargs = {
        "bbox_inches": bbox,  # bounding box method
        "facecolor": fig.get_facecolor(),
        "transparent": True,  # No background colour
        "dpi": dpi,
    }
    # TODO: investigate savefig preventing update of plot in qt5 backend until click on fig

    if fig_fmt in [".pdf", ".eps"]:
        metadata = {  # Cleaning this metadata makes version control easier
            "Creator": "",
            "Producer": "",
            "CreationDate": None,
        }  # TODO: allow users to specify their own metadata
        fig.savefig(fpath, metadata=metadata, **common_kwargs)
    elif fig_fmt == ".svg":
        with plt.rc_context(
            {"svg.fonttype": "none"},
        ):  # force text to be text, not paths
            fig.savefig(fpath, **common_kwargs)
    elif fig_fmt == ".png":
        alpha = 0 if transparent_png else 1
        axes = fig.get_axes()
        fig.patch.set_alpha(alpha)
        for ax in axes:
            ax.patch.set_alpha(alpha)

        fig.savefig(fpath, **common_kwargs)
    else:
        msg = f"File format {fig_fmt} not recognised"
        raise ValueError(msg)


def add_cm_overlay_grid(
    figure: mpl.figure.Figure,
    width_cm: float | None = None,
    height_cm: float | None = None,
) -> tuple[
    mpl.axes.Axes,
    mpl.collections.PathCollection,
    mpl.collections.PathCollection,
    mpl.collections.PathCollection,
]:
    """Add an overlay to view the cm size of all items on the figure.

    :param figure: figure to overlay a grid onto
    :type figure: matplotlib.figures.Figure
    :param width_cm: Width of the figure in cm (default None, uses figure size)
    :type width_cm: float
    :param height_cm: Height of the figure in cm (default None, uses figure size)
    :type height_cm: float
    :return: Tuple containing the axes and scatter collections for 1cm, 0.5cm, and 5cm markers
    :rtype: tuple[mpl.axes.Axes,
                  mpl.collections.PathCollection,
                  mpl.collections.PathCollection,
                  mpl.collections.PathCollection]
    """
    # Allow user to specify what the position is meant to be
    # rather than what it actually is
    width_cm_actual, height_cm_actual = locations.inch_to_cm(figure.get_size_inches())
    width_cm = width_cm_actual if width_cm is None else width_cm
    height_cm = height_cm_actual if height_cm is None else height_cm

    # Create an axes spanning the entire grid
    ax = figure.add_axes(
        [0, 0, 1, 1],
        label="cm_overlay",
        frameon=False,
    )  # No axis lines
    ax.set_navigate(
        False,
    )  # Make the zoom/panning interactive tool not apply to this axes

    # Set limits to match the cm size of the figure
    ax.set_ylim([0, height_cm])
    ax.set_xlim([0, width_cm])
    ax.invert_yaxis()  # invert y origin to be upper to match the coordinate system

    # Generate positions of each cm marker
    n_widths = np.ceil(width_cm).astype(int) + 1
    n_heights = np.ceil(height_cm).astype(int) + 1
    xlocs = np.arange(n_widths)
    ylocs = np.arange(n_heights)

    # Create 1cm mesh grid, make the 1cm markers and smaller 0.5 cm markers
    mesh = np.meshgrid(xlocs, ylocs)
    # Plot 1cm markers
    sax_1cm = ax.scatter(mesh[0], mesh[1], alpha=0.3, color="k", s=5, marker="+")

    # Plot 0.5cm markers
    sax_05cm = ax.scatter(
        mesh[0] + 0.5, mesh[1] + 0.5, marker="x", color="k", alpha=0.3, s=5, lw=0.3
    )

    # Create 5cm mesh grid
    mesh5 = np.meshgrid(xlocs[::5], ylocs[::5])
    sax_5cm = ax.scatter(mesh5[0], mesh5[1], color="k", marker="+", lw=2, alpha=0.3)
    return ax, sax_1cm, sax_05cm, sax_5cm


def set_figure_size_cm(
    fig: mpl.figure.Figure,
    w: float,
    h: float,
) -> None:
    """Set the size of a figure in cm.

    :param fig: Figure to change
    :type fig: matplotlib.figures.Figure
    :param w: Width in cm
    :type w: float
    :param h: Height in cm
    :type h: float
    """
    fig.set_size_inches(w=locations.cm_to_inch(w), h=locations.cm_to_inch(h))
