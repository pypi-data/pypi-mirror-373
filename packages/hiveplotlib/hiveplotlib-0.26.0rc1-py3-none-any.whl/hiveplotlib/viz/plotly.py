# plotly.py

"""
``plotly``-backend visualizations in ``hiveplotlib``.
"""

try:
    import plotly.graph_objects as go
except ImportError as ie:  # pragma: no cover
    raise ImportError(
        "plotly not installed, but can be installed by running `pip install hiveplotlib[plotly]`"
    ) from ie

import warnings
from typing import Hashable, List, Literal, Optional, Union

import numpy as np
import pandas as pd
from matplotlib.colors import hex2color, to_hex

from hiveplotlib import P2CP, BaseHivePlot, HivePlot
from hiveplotlib.utils import polar2cartesian
from hiveplotlib.viz.base import (
    edge_viz_preparation,
    get_axis_label_alignment,
    get_hover_axis_metadata,
    hover_input_check,
)
from hiveplotlib.viz.input_checks import input_check


def _plotly_fig_setup(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[go.Figure] = None,
    buffer: float = 0.3,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    layout_kwargs: Optional[dict] = None,
) -> go.Figure:
    """
    Set up ``plotly`` figure and perform any further adjustments based on other parameter settings.

    :param hive_plot: ``HivePlot`` instance to plot. Should never take a ``P2CP`` instance.
    :param fig: figure to modify, generates one if ``None`` provided.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True`` hides the
        x and y axes).
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :return: resulting ``plotly`` figure.
    """
    if layout_kwargs is None:
        layout_kwargs = {}

    fig_update_kwargs = {}

    # can only center the plot if you have axes
    if center_plot and hive_plot.max_polar_end is not None:
        # center plot at (0, 0)
        max_radius = hive_plot.max_polar_end
        # throw in a minor buffer
        buffer_radius = buffer * max_radius
        max_radius += buffer_radius

        fig_update_kwargs["xaxis_range"] = [-max_radius, max_radius]
        fig_update_kwargs["yaxis_range"] = [-max_radius, max_radius]

    if axes_off:
        fig_update_kwargs["xaxis"] = {"visible": False}
        fig_update_kwargs["yaxis"] = {"visible": False}
    else:
        fig_update_kwargs["xaxis"] = {"visible": True}
        fig_update_kwargs["yaxis"] = {"visible": True}
        fig_update_kwargs["plot_bgcolor"] = None

    # allow for plotting onto specified figure
    if fig is None:
        layout_kwargs.setdefault("autosize", False)
        layout_kwargs.setdefault("showlegend", False)
        layout_kwargs.setdefault("plot_bgcolor", "white")
        layout_kwargs.setdefault("hovermode", False)
        layout_kwargs.setdefault("dragmode", "pan")
        layout_kwargs.setdefault("height", height)
        layout_kwargs.setdefault("width", width)
        fig = go.Figure(layout=layout_kwargs)

    fig.update_layout(**fig_update_kwargs)

    return fig


def _opacity_color_handler(color: str, opacity: float) -> str:
    """
    Convert a named CSS color or hex color to a ``plotly`` compatible color with an ``opacity`` value as an RGBA string.

    .. note::
        If providing an RGB / HSL / HSV string, then no revisions will be made to the input colors, as opacity is
        already exposed for these string (e.g. RGBA / HSLA / HSVA strings, respectively).

    :param color: input color string.
    :param opacity: opacity of line to set. Must be in [0, 1].
    :return: string RGBA (e.g. red, green, blue, alpha) color in the format ``"rgba(red,green,blue,alpha)"`` that
        ``plotly`` supports, where the alpha value will be ``opacity``.
    """
    assert 0 <= opacity <= 1, "Parameter `opacity` must be in [0, 1]."
    if "(" in color:
        return color

    if color[0] != "#":
        color = to_hex(color)

    # RGB values come in originally in [0, 1] but plotly expects [0, 255] range
    rgb_values = np.array(hex2color(color)) * 255
    red = int(rgb_values[0])
    green = int(rgb_values[1])
    blue = int(rgb_values[2])

    return f"rgba({red},{green},{blue},{opacity})"


def axes_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[go.Figure] = None,
    line_width: float = 1.5,
    opacity: float = 1.0,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.25,
    axes_labels_fontsize: float = 16,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    layout_kwargs: Optional[dict] = None,
    hover: bool = True,
    label_kwargs: Optional[dict] = None,
    **line_kwargs,
) -> go.Figure:
    """
    Visualize axes in a ``HivePlot`` or ``P2CP`` instance with ``plotly``.

    .. note::
        The ``line_width`` parameter corresponds to the standard ``width`` parameter for plotly lines. We are exposing
        this parameter with a different name because ``width`` is already the standard name for *figure* width
        throughout ``hiveplotlib.viz``.

        ``plotly`` out of the box does not support standard ``opacity`` for its line plots like it does for scatter
        plots, but it does support providing an alpha channel in RGBA / HSVA / HSLA strings. The ``opacity`` parameter
        in this function call will behave as ``opacity`` behaves for ``plotly`` scatter plots, as long as the
        user-provided colors are either standard named CSS colors (e.g. "blue", "navy", "green") or hex colors.

        Users who prefer to provide colors as multi-channel RGBA / HSVA / HSLA strings will override the
        ``opacity`` parameter. For more on how to provide multi-channel color strings, see the ``plotly`` docs for the
        `color parameter for lines <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.marker.html#plotly.graph_objects.scatter.marker.Line.color>`_.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw axes.
    :param fig: default ``None`` builds new figure. If a figure is specified, axes will be drawn on that figure.
    :param line_width: width of axes.
    :param opacity: opacity of edges. Must be in [0, 1].
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True`` hides the
        x and y axes).
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param hover: whether to add hover information or not for axes. ``False`` excludes hover information. Default
        ``True``. Hover info will appear over axes labels. Only works currently for Hive Plots, not P2CPs.
    :param label_kwargs: additional kwargs passed to the ``textfont`` parameter of ``plotly.graph_objects.Scatter()``.
        For examples of parameter options, see the `plotly docs <https://plotly.com/python/text-and-annotations/>`__.
    :param line_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Line>`__
        call.
    :return: ``plotly`` figure.
    """
    # some default kwargs for the axes
    line_kwargs.setdefault("color", "black")
    line_kwargs.setdefault("width", line_width)

    # opacity handling for the line color
    line_kwargs["color"] = _opacity_color_handler(
        color=line_kwargs["color"],
        opacity=opacity,
    )

    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    if label_kwargs is None:
        label_kwargs = {}

    fig = _plotly_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        layout_kwargs=layout_kwargs,
    )

    if show_axes_labels:
        fig = label_axes(
            instance=instance,
            fig=fig,
            center_plot=False,
            axes_labels_buffer=axes_labels_buffer,
            axes_labels_fontsize=axes_labels_fontsize,
            axes_off=axes_off,
            hover=hover,
            **label_kwargs,
        )

    for axis in hive_plot.axes.values():
        to_plot = np.vstack((axis.start, axis.end))
        fig.add_trace(
            go.Scatter(
                x=to_plot[:, 0],
                y=to_plot[:, 1],
                mode="lines",
                line=line_kwargs,
                showlegend=False,
                name="",  # stops "trace j" from showing up next to hover output
                hoverinfo="skip",
            )
        )

    return fig


def label_axes(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[go.Figure] = None,
    axes_labels_buffer: float = 1.25,
    axes_labels_fontsize: float = 16,
    buffer: float = 0.3,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    layout_kwargs: Optional[dict] = None,
    hover: bool = True,
    **label_kwargs,
) -> go.Figure:
    """
    Visualize axis labels in a ``HivePlot`` or ``P2CP`` instance with ``plotly``.

    For ``HivePlot`` instances, each axis' ``long_name`` attribute will be used. For ``P2CP`` instances, column names in
    the ``data`` attribute will be used.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw nodes.
    :param fig: default ``None`` builds new figure. If a figure is specified, axis labels will be drawn on that figure.
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True`` hides the
        x and y axes).
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param hover: whether to add hover information or not over axes labels. ``False`` excludes hover information.
        Default ``True``. Only works currently for Hive Plots, not P2CPs.
    :param label_kwargs: additional kwargs passed to the ``textfont`` parameter of ``plotly.graph_objects.Scatter()``.
        For examples of parameter options, see the `plotly docs <https://plotly.com/python/text-and-annotations/>`__.
    :return: ``plotly`` figure.
    """
    # set default kwargs for labels
    label_kwargs.setdefault("size", axes_labels_fontsize)
    label_kwargs.setdefault("color", "black")

    if layout_kwargs is None:
        layout_kwargs = {}

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    fig = _plotly_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        layout_kwargs=layout_kwargs,
    )

    # single warning of unsupported case outside of for loop
    if hover is True and name == "P2CP":
        warnings.warn(
            "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
            stacklevel=2,
        )

    for axis in hive_plot.axes.values():
        hover_kwargs = {}
        if hover is True and name != "P2CP":
            custom_data = get_hover_axis_metadata(axis=axis)

            long_name_idx = np.where(custom_data.columns == "long_name")[0][0]
            hovertemplate = [f"<b>Axis: %{{customdata[{long_name_idx}]}}</b>"] + [
                f"{name}: %{{customdata[{i}]}}"
                for i, name in enumerate(custom_data)
                if name not in ["long_name"]
            ]

            hovertemplate = "<br>".join(hovertemplate)
            hover_kwargs.setdefault("hovertemplate", hovertemplate)
            hover_kwargs.setdefault("customdata", custom_data)
            layout_kwargs.setdefault("hovermode", "closest")
        else:
            hover_kwargs["hoverinfo"] = "skip"

        # choose horizontal and vertical alignment based on axis angle in [0, 360)
        vertical_alignment, horizontal_alignment = get_axis_label_alignment(
            axis=axis,
            backend="plotly",
        )
        x, y = polar2cartesian(axes_labels_buffer * axis.polar_end, axis.angle)
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="text",
                text=axis.long_name,
                textposition=f"{vertical_alignment} {horizontal_alignment}",
                textfont=dict(**label_kwargs),
                showlegend=False,
                name="",  # stops "trace j" from showing up next to hover output
                **hover_kwargs,
            )
        )

    return fig


def node_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[go.Figure] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    layout_kwargs: Optional[dict] = None,
    hover: bool = True,
    **scatter_kwargs,
) -> go.Figure:
    """
    Visualize of nodes in a ``HivePlot`` or ``P2CP`` instance that have been placed on their axes in ``plotly``.

    .. note::
        If ``instance`` is a ``HivePlot``, then users can provide node-specific data to plotting keyword arguments by
        providing column names from the ``HivePlot.nodes.data`` DataFrame as values in either the
        ``HivePlot.nodes.node_viz_kwargs`` dictionary via ``HivePlot.update_node_viz_kwargs()`` or in this call in the
        provided ``scatter_kwargs``.

        If ``instance`` is a ``HivePlot``, then any provided node plotting keyword arguments in
        ``HivePlot.nodes.node_viz_kwargs`` will be prioritized over any provided ``scatter_kwargs``.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw nodes.
    :param fig: default ``None`` builds new figure. If a figure is specified, nodes will be drawn on that figure.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True``
        hides the x and y axes).
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param hover: whether to add hover information or not for nodes. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param scatter_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `plotly.graph_objects.scatter.Marker() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Marker>`__
        call. Node data values can also be used, see note above for more details.
    :return: ``plotly`` figure.
    """
    # some default kwargs for the axes
    scatter_kwargs.setdefault("color", "black")
    scatter_kwargs.setdefault("opacity", 0.8)
    scatter_kwargs.setdefault("size", 8)

    hive_plot, name, _ = input_check(instance, objects_to_plot="nodes")

    if layout_kwargs is None:
        layout_kwargs = {}

    hover_kwargs = {}
    if hover is True:
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        else:
            hovertemplate = ["<b>Node: %{customdata[0]}</b>"] + [
                f"{name}: %{{customdata[{i}]}}"
                for i, name in enumerate(hive_plot.nodes.data.columns)
                if name not in [hive_plot.nodes.unique_id_column]
            ]

            hovertemplate = "<br>".join(hovertemplate)
            hover_kwargs.setdefault("hovertemplate", hovertemplate)
            layout_kwargs.setdefault("hovermode", "closest")
    else:
        hover_kwargs["hoverinfo"] = "skip"

    fig = _plotly_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        layout_kwargs=layout_kwargs,
    )

    for axis in hive_plot.axes.values():
        # add to / overwrite any provided scatter kwargs with the NodeCollection ``node_viz_kwargs``
        final_scatter_kwargs = scatter_kwargs.copy() | hive_plot.nodes.node_viz_kwargs
        # if any kwarg value corresponds to a node data column name, use the node data values
        for kw, val in final_scatter_kwargs.items():
            # if value is name of column, then propagate those values as a 1d array (e.g. value per node)
            if isinstance(val, Hashable) and val in hive_plot.nodes.data.columns:
                final_scatter_kwargs[kw] = axis.node_placements[val].to_numpy()
            # otherwise pass on the kwarg normally
            else:
                final_scatter_kwargs[kw] = val
        to_plot = axis.node_placements
        if to_plot.shape[0] > 0:
            fig.add_trace(
                go.Scatter(
                    x=to_plot["x"].to_numpy(),
                    y=to_plot["y"].to_numpy(),
                    customdata=to_plot.drop(columns=["x", "y", "rho"]).to_numpy(),
                    mode="markers",
                    marker=final_scatter_kwargs,
                    showlegend=False,
                    name="",  # stops "trace j" from showing up next to hover output
                    **hover_kwargs,
                )
            )

    return fig


def edge_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[go.Figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    line_width: Optional[float] = None,
    opacity: Optional[float] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    layout_kwargs: Optional[dict] = None,
    hover: bool = True,
    **edge_kwargs,
) -> go.Figure:
    """
    Visualize constructed edges in a ``HivePlot`` or ``P2CP`` instance with ``plotly``.

    .. note::
        If ``instance`` is a ``HivePlot``, then users can provide edge-specific data to plotting keyword arguments by
        providing column names from the ``HivePlot.edges.data`` DataFrame as values to one of the following options:

        1. ``HivePlot.edge_plotting_keyword_arguments`` attribute via
           ``HivePlot.update_edge_plotting_keyword_arguments()``.

        2. ``HivePlot.edges.edge_viz_kwargs`` attribute via ``HivePlot.edges.update_edge_viz_kwargs()``.

        3. In this call in the provided ``edge_kwargs``.

        If ``instance`` is a ``HivePlot``, then edge keyword arguments will be prioritized according to the following
        hierarchy:

        The most prioritized arguments are the arguments stored in the hive plot ``hive_plot_edges`` attribute, followed
        by the provided ``edge_kwargs``, then the edge keyword argument hierarchy set by the hive plot's
        ``edge_kwarg_hierarchy`` attribute, and finally the ``HivePlot.edges.edge_viz_kwargs``.

        If any keyword arguments in the ``hive_plot_edges`` attribute are also provided in this function's
        ``edge_kwargs``, then a warning will be raised.

        The ``line_width`` parameter corresponds to the standard ``width`` parameter for plotly lines. We are exposing
        this parameter with a different name because ``width`` is already the standard name for *figure* width
        throughout ``hiveplotlib.viz``.

        ``plotly`` out of the box does not support standard ``opacity`` for its line plots like it does for scatter
        plots, but it does support providing an alpha channel in RGBA / HSVA / HSLA strings. The ``opacity`` parameter
        in this function call will behave as ``opacity`` behaves for ``plotly`` scatter plots, as long as the
        user-provided colors are either standard named CSS colors (e.g. "blue", "navy", "green") or hex colors.

        Users who prefer to provide colors as multi-channel RGBA / HSVA / HSLA strings will override the
        ``opacity`` parameter. For more on how to provide multi-channel color strings, see the ``plotly`` docs for the
        `color parameter for lines <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.marker.html#plotly.graph_objects.scatter.marker.Line.color>`_.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param fig: default ``None`` builds new figure. If a figure is specified, edges will be drawn on that figure.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param line_width: width of edges. Default ``None`` sets line width to ``1.5`` if not provided by any other keyword
        arguments.
    :param opacity: opacity of edges. Must be in [0, 1]. Default ``None`` sets opacity to ``0.5`` if not provided by any
        other keyword arguments.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True``
        hides the x and y axes).
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param hover: whether to add hover information or not for edges. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` / :py:meth:`hiveplotlib.P2CP.build_edges` or
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` / :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will take
        priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` /
        :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.marker.html#plotly.graph_objects.scatter.marker.Line>`__
        call. Edge data values can also be used, see note above for more details.
    :return: ``plotly`` figure.
    """
    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="edges")

    if hover is True and name == "P2CP":
        warnings.warn(
            "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
            stacklevel=2,
        )

    fig = _plotly_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        layout_kwargs=layout_kwargs,
    )

    # stop plotting if there are no edges to plot
    if warning_raised:
        return fig

    # p2cp warnings only need to happen once per tag
    #  because all axes behave in unison
    already_warned_p2cp_tags = []

    # grouping elements of legend by tag, plotting each group as one element in the legend
    already_added_legend_tags = []

    edge_viz_preparation_kwargs = {}

    # if doing data-based opacity (via an edge df column name),
    #   be sure to exclude from default kwargs for later calculation
    if isinstance(opacity, str):
        edge_viz_preparation_kwargs["default_line_color"] = "black"
    else:
        opacity_to_use = 0.5 if opacity is None else opacity
        edge_viz_preparation_kwargs["default_line_color"] = _opacity_color_handler(
            color="black",
            opacity=opacity_to_use,  # default opacity if not provided
        )
    # if doing data-based line-width (via an edge df column name),
    #   be sure to exclude from default kwargs for later calculation in each trace
    if isinstance(line_width, str):
        edge_viz_preparation_kwargs["include_line_width"] = False

    for a0 in hive_plot.hive_plot_edges:
        for a1 in hive_plot.hive_plot_edges[a0]:
            # use all tags if no specific tags requested
            # otherwise, make sure we have a flat list of tags
            tags_to_plot = (
                hive_plot.hive_plot_edges[a0][a1].keys()
                if tags is None
                else list(np.array(tags).flatten())
            )

            for tag in tags_to_plot:
                hover_kwargs = {}
                if hover is True and hive_plot.edges is not None:
                    from_col_number = np.where(
                        hive_plot.edges._data[tag].columns
                        == hive_plot.edges.from_column_name
                    )[0][0]
                    to_col_number = np.where(
                        hive_plot.edges._data[tag].columns
                        == hive_plot.edges.to_column_name
                    )[0][0]
                    right_arrow = "&#x27A1;"
                    hovertemplate = [
                        f"<b>Edge: %{{customdata[{from_col_number}]}} {right_arrow} "
                        f"%{{customdata[{to_col_number}]}}</b>"
                    ] + [
                        f"{name}: %{{customdata[{i}]}}"
                        for i, name in enumerate(hive_plot.edges._data[tag].columns)
                        if name
                        not in [
                            hive_plot.edges.from_column_name,
                            hive_plot.edges.to_column_name,
                        ]
                    ]

                    hovertemplate = "<br>".join(hovertemplate)
                    hover_kwargs.setdefault("hovertemplate", hovertemplate)
                    layout_kwargs.setdefault("hovermode", "closest")
                else:
                    hover_kwargs["hoverinfo"] = "skip"
                # propagate opacity and line width if provided by user (to be custom handled later)
                if line_width is not None:
                    edge_kwargs["line_width"] = line_width
                if opacity is not None:
                    edge_kwargs["opacity"] = opacity

                temp_edge_kwargs, already_warned_p2cp_tags = edge_viz_preparation(
                    hive_plot=hive_plot,
                    name=name,
                    from_axis=a0,
                    to_axis=a1,
                    tag=tag,
                    already_warned_p2cp_tags=already_warned_p2cp_tags,
                    edge_kwargs=edge_kwargs,
                    line_width_name="width",
                    line_alpha_name="opacity",
                    line_color_name="color",
                    include_line_alpha=False,
                    default_line_width=line_width,
                    **edge_viz_preparation_kwargs,
                )

                # add to / overwrite any provided edge kwargs with the Edges ``edge_viz_kwargs``
                if hive_plot.edges is not None:
                    # priority queue of edge kwargs
                    final_edge_kwargs = (
                        hive_plot.edges.edge_viz_kwargs[tag]
                        | temp_edge_kwargs.copy()
                        | hive_plot.hive_plot_edges[a0][a1][tag]["edge_kwargs"]
                    )
                else:
                    final_edge_kwargs = temp_edge_kwargs.copy()
                    # add any hive plot edge kwargs (if existing)
                    if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                        final_edge_kwargs |= hive_plot.hive_plot_edges[a0][a1][tag][
                            "edge_kwargs"
                        ]

                # set default values if not provided
                if line_width is None:
                    final_edge_kwargs.setdefault("line_width", 1.5)
                if opacity is None:
                    final_edge_kwargs.setdefault("opacity", 0.5)
                final_edge_kwargs.setdefault(
                    "color", edge_viz_preparation_kwargs["default_line_color"]
                )

                if hive_plot.edges is not None:
                    # if any kwarg value corresponds to an edge data column name, use the edge data values
                    for kw, val in final_edge_kwargs.items():
                        # if value is name of column, then propagate those values as a 1d array (e.g. value per edge)
                        if (
                            isinstance(val, Hashable)
                            and val in hive_plot.edges._data[tag].columns
                        ):
                            relevant_edges = hive_plot.edges.relevant_edges[a0][a1][tag]
                            final_edge_kwargs[kw] = (
                                hive_plot.edges._data[tag]
                                .loc[relevant_edges, val]
                                .to_numpy()
                            )
                        # otherwise pass on the kwarg normally
                        else:
                            final_edge_kwargs[kw] = val

                # only run plotting of edges that exist
                if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                    # trace name important for p2cp legend
                    #   otherwise disruptive on hive plot hover info
                    trace_name = str(tag) if name == "P2CP" else ""
                    # make sure we fix `line_width`` name back to `width` before plotting
                    if "line_width" in final_edge_kwargs:
                        final_edge_kwargs["width"] = final_edge_kwargs["line_width"]
                        del final_edge_kwargs["line_width"]

                    # grab the requested array of discretized curves
                    edge_arr = hive_plot.hive_plot_edges[a0][a1][tag]["curves"]
                    # if there's no actual edges there, don't plot
                    if edge_arr.size > 0:
                        split_arrays = np.split(
                            edge_arr, np.where(np.isnan(edge_arr[:, 0]))[0]
                        )[:-1]  # last element is a [NaN, NaN] array
                        # no plotly support for multiline with unique kwargs, so add one at a time
                        for i, arr in enumerate(split_arrays):
                            if tag in already_added_legend_tags:
                                showlegend = False
                            else:
                                showlegend = True
                                already_added_legend_tags.append(tag)
                            # wrangle specific value for any list-like kwargs
                            sub_final_kwargs = final_edge_kwargs.copy()
                            for kw in sub_final_kwargs:
                                if pd.api.types.is_list_like(sub_final_kwargs[kw]):
                                    sub_final_kwargs[kw] = sub_final_kwargs[kw][i]
                            # make sure we fix the final edge colors with opacity modification
                            sub_final_kwargs["color"] = _opacity_color_handler(
                                color=sub_final_kwargs["color"],
                                opacity=sub_final_kwargs["opacity"],
                            )
                            # kill opacity now that we've modified the color
                            del sub_final_kwargs["opacity"]
                            custom_data_kwargs = {}
                            if hover is True and hive_plot.edges is not None:
                                custom_data = hive_plot.edges._data[tag][
                                    hive_plot.edges.relevant_edges[a0][a1][tag]
                                ].iloc[i, :]
                                custom_data_kwargs["customdata"] = [
                                    custom_data
                                ] * arr.shape[0]
                            fig.add_trace(
                                go.Scatter(
                                    x=arr[:, 0],
                                    y=arr[:, 1],
                                    mode="lines",
                                    legendgroup=str(tag),
                                    line=dict(**sub_final_kwargs),
                                    showlegend=showlegend,
                                    name=trace_name,
                                    **hover_kwargs,
                                    **custom_data_kwargs,
                                )
                            )

    return fig


def hive_plot_viz(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[go.Figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.25,
    axes_labels_fontsize: float = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    label_kwargs: Optional[dict] = None,
    layout_kwargs: Optional[dict] = None,
    hover: Union[
        bool,
        Literal["nodes", "edges", "axes"],
        list[Literal["nodes", "edges", "axes"],],
    ] = True,
    **edge_kwargs,
) -> go.Figure:
    """
    Create default ``plotly`` visualization of a ``HivePlot`` instance.

    .. note::
        Users can provide node-specific data to plotting keyword arguments by providing column names from the
        ``HivePlot.nodes.data`` DataFrame as values in either the ``HivePlot.nodes.node_viz_kwargs`` dictionary via
        ``HivePlot.update_node_viz_kwargs()`` or in this call in the provided ``node_kwargs``.

        Any provided node plotting keyword arguments in ``HivePlot.nodes.node_viz_kwargs`` will be prioritized over any
        provided ``node_kwargs``.

        Users can provide edge-specific data to plotting keyword arguments by providing column names from the
        ``HivePlot.edges.data`` DataFrame as values to one of the following options:

        1. ``HivePlot.edge_plotting_keyword_arguments`` attribute via
           ``HivePlot.update_edge_plotting_keyword_arguments()``.

        2. ``HivePlot.edges.edge_viz_kwargs`` attribute via ``HivePlot.edges.update_edge_viz_kwargs()``.

        3. In this call in the provided ``edge_kwargs``.

        Edge keyword arguments will be prioritized according to the following hierarchy:

        The most prioritized arguments are the arguments stored in the hive plot ``hive_plot_edges`` attribute, followed
        by the provided ``edge_kwargs``, then the edge keyword argument hierarchy set by the hive plot's
        ``edge_kwarg_hierarchy`` attribute, and finally the ``HivePlot.edges.edge_viz_kwargs``.

        If any keyword arguments in the ``hive_plot_edges`` attribute are also provided in this function's
        ``edge_kwargs``, then a warning will be raised.

        The line width and opacity of axes can be changed by including the ``line_width`` and ``opacity`` parameters,
        respectively, in ``axes_kwargs``. See the documentation for :py:func:`hiveplotlib.viz.plotly.axes_viz()` for
        more information.

        If the line width and opacity of edges was not set in the original hive plot, then these parameters can be set
        by including the ``line_width`` and ``opacity`` parameters, respectively, as additional keyword arguments. See
        the documentation for :py:func:`hiveplotlib.viz.plotly.edge_viz()` for more information.

    :param hive_plot: ``HivePlot`` instance we want to visualize.
    :param fig: default ``None`` builds new figure. If a figure is specified, hive plot will be drawn on that figure.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for hive plot axes labels.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `plotly.graph_objects.scatter.Marker() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Marker>`__
        call. Node data values can also be used, see note above for more details.
    :param axes_kwargs: additional params that will be applied to all hive plot axes. This includes the ``line_width``
        and ``opacity`` parameters in :py:func:`hiveplotlib.viz.plotly.axes_viz()`. Note, these are kwargs that affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Line>`__
        call.
    :param label_kwargs: additional kwargs passed to the ``textfont`` parameter of ``plotly.graph_objects.Scatter()``.
        For examples of parameter options, see the `plotly docs <https://plotly.com/python/text-and-annotations/>`__.
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param hover: whether to add hover information or not for nodes, edges, and / or axes. ``False`` excludes all hover
        information, while default ``True`` includes node, edge, and axis hover information. Providing the value
        ``"nodes"`` / ``"edges"`` / ``"axes"`` adds hover information ONLY for nodes / edges / axes. Users can also
        provide a list of a subset of these values (e.g. providing ``["nodes", "edges"]`` would show all hover info
        except for axes).
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` or :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()`
        will take priority). This includes the ``line_width`` and ``opacity`` parameters in
        :py:func:`hiveplotlib.viz.plotly.edge_viz()`. To overwrite previously set kwargs, see
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.marker.html#plotly.graph_objects.scatter.marker.Line>`__
        call. Edge data values can also be used, see note above for more details.
    :raises InvalidHoverVariableError: if invalid input provided to ``hover`` parameter.
    :return: ``plotly`` figure.
    """
    hover_input_check(hover=hover)

    if layout_kwargs is None:
        layout_kwargs = {}

    # make sure hover shows up if hover not False
    if hover is not False:
        layout_kwargs["hovermode"] = "closest"

    if node_kwargs is None:
        node_kwargs = {}

    if axes_kwargs is None:
        axes_kwargs = {}

    edge_hover_kwargs = {"hover": False}
    if (
        hover is True
        or hover == "edges"
        or (pd.api.types.is_list_like(hover) and "edges" in hover)
    ):
        edge_hover_kwargs["hover"] = True

    fig = edge_viz(
        instance=hive_plot,
        fig=fig,
        width=width,
        height=height,
        tags=tags,
        center_plot=False,
        layout_kwargs=layout_kwargs,
        **edge_hover_kwargs,
        **edge_kwargs,
    )

    axes_hover_kwargs = {"hover": False}
    if (
        hover is True
        or hover == "axes"
        or (pd.api.types.is_list_like(hover) and "axes" in hover)
    ):
        axes_hover_kwargs["hover"] = True

    axes_viz(
        instance=hive_plot,
        fig=fig,
        center_plot=False,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        label_kwargs=label_kwargs,
        **axes_hover_kwargs,
        **axes_kwargs,
    )

    node_hover_kwargs = {"hover": False}
    if (
        hover is True
        or hover == "nodes"
        or (pd.api.types.is_list_like(hover) and "nodes" in hover)
    ):
        node_hover_kwargs["hover"] = True

    # do the centering / redim-ing if requested only on the last call, otherwise it will be overridden
    node_viz(
        instance=hive_plot,
        fig=fig,
        buffer=buffer,
        center_plot=center_plot,
        axes_off=axes_off,
        **node_hover_kwargs,
        **node_kwargs,
    )

    return fig


def p2cp_viz(
    p2cp: P2CP,
    fig: Optional[go.Figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.25,
    axes_labels_fontsize: float = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    label_kwargs: Optional[dict] = None,
    layout_kwargs: Optional[dict] = None,
    **edge_kwargs,
) -> go.Figure:
    """
    Create default ``plotly`` visualization of a ``P2CP`` instance.

    .. note::
        The line width and opacity of axes can be changed by including the ``line_width`` and ``opacity`` parameters,
        respectively, in ``axes_kwargs``. See the documentation for :py:func:`hiveplotlib.viz.plotly.axes_viz()` for
        more information.

        If the line width and opacity of edges was not set in the original P2CP, then these parameters can be set
        by including the ``line_width`` and ``opacity`` parameters, respectively, as additional keyword arguments. See
        the documentation for :py:func:`hiveplotlib.viz.plotly.edge_viz()` for more information.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: default ``None`` builds new figure. If a figure is specified, P2CP will be drawn on that figure.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``p2cp``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the P2CP axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for P2CP axes labels.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``plotly`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all P2CP nodes. Note, these are kwargs that
        affect a `plotly.graph_objects.scatter.Marker() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Marker>`__
        call.
    :param axes_kwargs: additional params that will be applied to all P2CP axes. This includes the ``line_width``
        and ``opacity`` parameters in :py:func:`hiveplotlib.viz.plotly.axes_viz()`. Note, these are kwargs that affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.html#plotly.graph_objects.scatter.Line>`__
        call.
    :param label_kwargs: additional kwargs passed to the ``textfont`` parameter of ``plotly.graph_objects.Scatter()``.
        For examples of parameter options, see the `plotly docs <https://plotly.com/python/text-and-annotations/>`__.
    :param layout_kwargs: additional values for the ``layout`` parameter to be called in
        `plotly.graph_objects.Figure() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html>`__
        call. Note, if ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and
        ``height`` parameters.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.P2CP.build_edges()` or :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will
        take priority). This includes the ``line_width`` and ``opacity`` parameters in
        :py:func:`hiveplotlib.viz.plotly.edge_viz()`. To overwrite previously set kwargs, see
        :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `plotly.graph_objects.scatter.Line() <https://plotly.com/python-api-reference/generated/plotly.graph_objects.scatter.marker.html#plotly.graph_objects.scatter.marker.Line>`__
        call.
    :return: ``plotly`` figure.
    """
    if node_kwargs is None:
        node_kwargs = {}

    if axes_kwargs is None:
        axes_kwargs = {}

    if "hover" in edge_kwargs:
        warnings.warn(
            "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
            stacklevel=2,
        )
        del edge_kwargs["hover"]

    fig = edge_viz(
        instance=p2cp,
        fig=fig,
        width=width,
        height=height,
        tags=tags,
        center_plot=False,
        layout_kwargs=layout_kwargs,
        hover=False,  # hover not currently supported for P2CPs
        **edge_kwargs,
    )

    axes_viz(
        instance=p2cp,
        fig=fig,
        center_plot=False,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        label_kwargs=label_kwargs,
        hover=False,  # hover not currently supported for P2CPs
        **axes_kwargs,
    )

    # do the centering / redim-ing if requested only on the last call, otherwise it will be overridden
    node_viz(
        instance=p2cp,
        fig=fig,
        buffer=buffer,
        center_plot=center_plot,
        axes_off=axes_off,
        hover=False,  # hover not currently supported for P2CPs
        **node_kwargs,
    )

    return fig


def p2cp_legend(
    p2cp: P2CP,
    fig: go.Figure,
    tags: Optional[Union[List[Hashable], Hashable]] = None,
    title: str = "Tags",
    **legend_kwargs,
) -> go.Figure:
    """
    Generate a legend for a ``P2CP`` instance, where entries in the legend will be tags of data added to the instance.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: ``plotly`` figure on which we will draw the legend.
    :param tags: which tags of data to include in the legend. Default ``None`` uses all tags under
        ``p2cp.tags``. This can be ignored unless explicitly wanting to *exclude* certain tags from the legend.
    :param title: title of the legend. Default "Tags".
    :param legend_kwargs: additional values for the ``legend`` parameter in the
        `plotly.graph_objects.update_layout() <https://plotly.com/python/reference/layout/#layout-legend>`__ call.
    :return: ``plotly`` figure.
    """
    legend_kwargs.setdefault("title", title)

    # need to convert tags to strings, as we needed to coax to strings to make them legend values with plotly
    tags = (
        [str(i) for i in p2cp.tags[:]]
        if tags is None
        else list(np.array(tags).flatten().astype(str))
    )

    fig.update_layout(showlegend=True, legend=legend_kwargs)

    return fig
