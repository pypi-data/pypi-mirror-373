"""
``holoviews`` visualizations in ``hiveplotlib``.

Currently, ``hiveplotlib`` supports a ``bokeh`` and ``matplotlib`` backend for ``holoviews``.
"""

# __all__ = []

try:
    import holoviews as hv
    from bokeh.models import HoverTool
    from holoviews import dim
except ImportError as ie:  # pragma: no cover
    raise ImportError(
        "`holoviews` not installed, but can be installed by running `pip install hiveplotlib[holoviews]`"
    ) from ie

import warnings
from typing import Hashable, List, Literal, Optional, Union, get_args

import numpy as np
import pandas as pd

from hiveplotlib import P2CP, BaseHivePlot, HivePlot
from hiveplotlib.utils import polar2cartesian
from hiveplotlib.viz.base import (
    __sanitize_dataframe_columns,
    edge_viz_preparation,
    get_axis_label_alignment,
    get_hover_axis_metadata,
    hover_input_check,
)
from hiveplotlib.viz.input_checks import input_check

SUPPORTED_BACK_ENDS = Literal["bokeh", "matplotlib"]


def _get_current_hv_backend() -> SUPPORTED_BACK_ENDS:
    """
    Get the current active ``holoviews`` backend.

    :return: string of current backend (i.e. ``bokeh`` or ``matplotlib``.)
    :raises ValueError: if anything other than one of the ``SUPPORTED_BACK_ENDS`` provided.
    """
    current_backend = hv.Store.current_backend
    assert current_backend in get_args(SUPPORTED_BACK_ENDS), (
        f"User using holoviews backend {current_backend} "
        f"but hiveplotlib currently only supports {get_args(SUPPORTED_BACK_ENDS)}"
    )
    return current_backend


def _holoviews_fig_modification(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: hv.Overlay,
    buffer: float = 0.3,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    axes_off: bool = True,
    xaxis: Optional[Literal["bare", "bottom", "top"]] = "bottom",
    yaxis: Optional[Literal["bare", "left", "right"]] = "left",
    overlay_kwargs: Optional[dict] = None,
) -> hv.Overlay:
    """
    Modify ``holoviews.Overlay`` with some Hiveplotlib-friendly defaults.

    :param hive_plot: ``HivePlot`` instance to plot. Should never take a ``P2CP`` instance.
    :param fig: ``holoviews.Overlay`` to modify.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10.
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10.
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param xaxis: placement of x axis. Only used if ``axes_off=False``.
    :param yaxis: placement of y axis. Only used if ``axes_off=False``.
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :return: ``holoviews.Overlay``.
    """
    backend = _get_current_hv_backend()

    if overlay_kwargs is None:
        overlay_kwargs = {}

    # set default title to nothing
    overlay_kwargs.setdefault("title", "")

    # only difference in different backend defaults is how to specify figure size
    if backend == "matplotlib":
        if width is None:
            width = 10
        if height is None:
            height = 10
        overlay_kwargs.setdefault("fig_inches", (width, height))
    elif backend == "bokeh":
        if width is None:
            width = 600
        if height is None:
            height = 600
        overlay_kwargs.setdefault("width", width)
        overlay_kwargs.setdefault("height", height)
        overlay_kwargs.setdefault("data_aspect", 1)
        overlay_kwargs.setdefault("data_aspect", 1)

    # can only center the plot if you have axes
    if center_plot and hive_plot.max_polar_end is not None:
        # center plot at (0, 0)
        max_radius = hive_plot.max_polar_end
        # throw in a minor buffer
        buffer_radius = buffer * max_radius
        max_radius += buffer_radius

        fig_bounds = (-max_radius, max_radius)
        overlay_kwargs.setdefault("xlim", fig_bounds)
        overlay_kwargs.setdefault("ylim", fig_bounds)

    if axes_off:
        overlay_kwargs["xaxis"] = None
        overlay_kwargs["yaxis"] = None
        if backend == "bokeh":
            overlay_kwargs["backend_opts"] = {"plot.outline_line_color": None}
    else:
        overlay_kwargs["xaxis"] = xaxis
        overlay_kwargs["yaxis"] = yaxis
        if backend == "bokeh":
            overlay_kwargs["backend_opts"] = {"plot.outline_line_color": "#e5e5e5"}

    return fig.opts(**overlay_kwargs)


def axes_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[hv.Overlay] = None,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    axes_off: bool = True,
    overlay_kwargs: Optional[dict] = None,
    hover: bool = True,
    text_kwargs: Optional[dict] = None,
    **segments_kwargs,
) -> hv.Overlay:
    """
    ``holoviews`` visualization of axes in a ``HivePlot`` or ``P2CP`` instance.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw axes.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param hover: whether to add hover information or not for axes. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param text_kwargs: additional kwargs passed to
        `holoviews.Text() <https://holoviews.org/reference/elements/bokeh/Text.html>`__ call.
    :param segments_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a `holoviews.Segments() <https://holoviews.org/reference/elements/bokeh/Segments.html>`__ call.
    :return: ``holoviews.Overlay``.
    """
    backend = _get_current_hv_backend()

    # some default kwargs for the axes
    segments_kwargs.setdefault("color", "black")
    if backend == "bokeh":
        segments_kwargs.setdefault("line_alpha", 0.5)
        segments_kwargs.setdefault("line_width", 1.5)
    elif backend == "matplotlib":
        segments_kwargs.setdefault("alpha", 0.5)
        segments_kwargs.setdefault("linewidth", 1.5)

    metadata_variables_to_exclude = ["long_name", "x_0", "x_1", "y_0", "y_1"]

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    if text_kwargs is None:
        text_kwargs = {}

    axis_dataframes = []
    axis_metadata_variables = set()
    for axis in hive_plot.axes.values():
        df = get_hover_axis_metadata(axis=axis)
        df["x_0"] = axis.start[0]
        df["y_0"] = axis.start[1]
        df["x_1"] = axis.end[0]
        df["y_1"] = axis.end[1]
        # drop all NaN columns to avoid pandas warning
        #  https://stackoverflow.com/questions/78957250/pandas-futurewarning-about-concatenating-dfs-with-nan-only-cols-seems-wrong
        axis_dataframes.append(df.dropna(axis=1, how="all"))

        # track all possible metadata variables
        metadata_variables = {
            i for i in df.columns if i not in metadata_variables_to_exclude
        }
        axis_metadata_variables = axis_metadata_variables.union(metadata_variables)

    axis_info = pd.concat(
        axis_dataframes
    ).drop_duplicates()  # each df has two redundant columns
    # make sure names are always hover compatible
    axis_info, original_to_sanitized_map = __sanitize_dataframe_columns(axis_info)
    if hover is True and backend == "bokeh":
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        else:
            variables = [
                f"<div>{i}: @{{{original_to_sanitized_map[i]}}}</div>"
                for i in sorted(axis_metadata_variables)
            ]
            tooltips = f"""
                    <div>
                        <b>Axis: @{{{original_to_sanitized_map["long_name"]}}}</b>
                            {"".join(variables)}
                    </div>
                """
            hover_tool = HoverTool(
                tooltips=tooltips,
                description="Axis Hover Info",
                attachment="vertical",
                anchor="bottom_right",
            )
            segments_kwargs["tools"] = [hover_tool]

    # fill NaN values with "N/A" string for hover tooltips
    axis_info = axis_info.fillna("N/A")
    axis_fig = hv.Segments(
        axis_info,
        kdims=[original_to_sanitized_map[i] for i in ["x_0", "y_0", "x_1", "y_1"]],
        vdims=[
            original_to_sanitized_map[i]
            for i in ["long_name"] + list(axis_metadata_variables)
            if i not in ["x_0", "x_1", "y_0", "y_1"]
        ],
    ).opts(
        **segments_kwargs,
    )

    if show_axes_labels:
        axis_fig = label_axes(
            instance=hive_plot,
            fig=axis_fig,
            center_plot=False,
            axes_labels_buffer=axes_labels_buffer,
            axes_labels_fontsize=axes_labels_fontsize,
            axes_off=axes_off,
            **text_kwargs,
        )

    # compose with existing fig if one was provided
    final_fig = fig * axis_fig if fig is not None else hv.Overlay(axis_fig)

    # holoviews modification comes at the end because we modify *existing* figures with .opts()
    return _holoviews_fig_modification(
        hive_plot=hive_plot,
        fig=final_fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
    )


def label_axes(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[hv.Overlay] = None,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    buffer: float = 0.3,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    axes_off: bool = True,
    overlay_kwargs: Optional[dict] = None,
    **text_kwargs,
) -> hv.Overlay:
    """
    ``holoviews`` visualization of axis labels in a ``HivePlot`` or ``P2CP`` instance.

    For ``HivePlot`` instances, each axis' ``long_name`` attribute will be used. For ``P2CP`` instances, column names in
    the ``data`` attribute will be used.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw axes.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param text_kwargs: additional kwargs passed to
        `holoviews.Text() <https://holoviews.org/reference/elements/bokeh/Text.html>`__ call.
    :return: ``holoviews.Overlay``.
    """
    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    label_plots = []
    for axis in hive_plot.axes.values():
        # choose horizontal and vertical alignment based on axis angle in [0, 360)
        vertical_alignment, horizontal_alignment = get_axis_label_alignment(
            axis=axis,
            backend="holoviews",
        )

        x, y = polar2cartesian(axes_labels_buffer * axis.polar_end, axis.angle)
        label = hv.Text(
            x=x,
            y=y,
            text=axis.long_name,
            fontsize=axes_labels_fontsize,
            halign=horizontal_alignment,
            valign=vertical_alignment,
            group="Labels",
        ).opts(
            **text_kwargs,
        )
        label_plots.append(label)

    labels_fig = hv.Overlay(label_plots)

    # compose with existing fig if one was provided
    final_fig = fig * labels_fig if fig is not None else labels_fig

    # holoviews modification comes at the end because we modify *existing* figures with .opts()
    return _holoviews_fig_modification(
        hive_plot=hive_plot,
        fig=final_fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
    )


def node_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[hv.Overlay] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    overlay_kwargs: Optional[dict] = None,
    hover: bool = True,
    **points_kwargs,
) -> hv.Overlay:
    """
    ``holoviews`` visualization of nodes in a ``HivePlot`` or ``P2CP`` instance that have been placed on their axes.

    .. note::
        If ``instance`` is a ``HivePlot``, then users can provide node-specific data to plotting keyword arguments by
        providing column names from the ``HivePlot.nodes.data`` DataFrame as values in either the
        ``HivePlot.nodes.node_viz_kwargs`` dictionary via ``HivePlot.update_node_viz_kwargs()`` or in this call in the
        provided ``points_kwargs``.

        If ``instance`` is a ``HivePlot``, then any provided node plotting keyword arguments in
        ``HivePlot.nodes.node_viz_kwargs`` will be prioritized over any provided ``points_kwargs``.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw nodes.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param hover: whether to add hover information or not for nodes. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param points_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `holoviews.Points() <https://holoviews.org/reference/elements/matplotlib/Points.html>`__ call.
        Node data values can also be used, see note above for more details.
    :return: ``holoviews.Overlay``.
    """
    backend = _get_current_hv_backend()

    # some default kwargs for the nodes
    points_kwargs.setdefault("color", "black")
    points_kwargs.setdefault("alpha", 0.8)
    if backend == "bokeh":
        points_kwargs.setdefault("size", 5)
    elif backend == "matplotlib":
        points_kwargs.setdefault("s", 35)

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="nodes")

    # stop plotting if there are no nodes to plot
    if warning_raised:
        if fig is None:
            return hv.Overlay()
        return fig

    if hover and backend == "bokeh":
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        else:
            variables = [
                f"<div>{i}: @{{{i}}}</div>"
                for i in hive_plot.nodes.data.columns
                if i not in [hive_plot.nodes.unique_id_column]
            ]
            tooltips = f"""
                <div>
                    <b>Node: @{{{hive_plot.nodes.unique_id_column}}}</b>
                        {"".join(variables)}
                </div>
            """
            hover_tool = HoverTool(
                tooltips=tooltips,
                description="Node Hover Info",
                attachment="horizontal",
            )
            points_kwargs.setdefault("tools", [hover_tool])

    points_plots = []
    # add to / overwrite any provided scatter kwargs with the NodeCollection ``node_viz_kwargs``
    # propagating column names as the column names because holoviews infers the data on its own
    final_points_kwargs = points_kwargs.copy() | hive_plot.nodes.node_viz_kwargs
    df_list = [
        axis.node_placements.drop(columns=["rho"])
        for axis in hive_plot.axes.values()
        if len(axis.node_placements) > 0
    ]
    if len(df_list) > 0:
        to_plot = pd.concat(df_list)
        if to_plot.shape[0] > 0:
            pt = hv.Points(to_plot, kdims=["x", "y"], group="Nodes").opts(
                **final_points_kwargs
            )
            points_plots.append(pt)

    points_fig = hv.Overlay(points_plots)

    # compose with existing fig if one was provided
    final_fig = fig * points_fig if fig is not None else points_fig

    # holoviews modification comes at the end because we modify *existing* figures with .opts()
    return _holoviews_fig_modification(
        hive_plot=hive_plot,
        fig=final_fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
    )


def edge_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[hv.Overlay] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    overlay_kwargs: Optional[dict] = None,
    hover: bool = True,
    **contours_kwargs,
) -> hv.Overlay:
    """
    ``holoviews`` visualization of constructed edges in a ``HivePlot`` or ``P2CP`` instance.

    .. note::
        If ``instance`` is a ``HivePlot``, then users can provide edge-specific data to plotting keyword arguments by
        providing column names from the ``HivePlot.edges.data`` DataFrame as values to one of the following options:

        1. ``HivePlot.edge_plotting_keyword_arguments`` attribute via
           ``HivePlot.update_edge_plotting_keyword_arguments()``.

        2. ``HivePlot.edges.edge_viz_kwargs`` attribute via ``HivePlot.edges.update_edge_viz_kwargs()``.

        3. In this call in the provided ``contours_kwargs``.

        If ``instance`` is a ``HivePlot``, then edge keyword arguments will be prioritized according to the following
        hierarchy:

        The most prioritized arguments are the arguments stored in the hive plot ``hive_plot_edges`` attribute, followed
        by the provided ``contours_kwargs``, then the edge keyword argument hierarchy set by the hive plot's
        ``edge_kwarg_hierarchy`` attribute, and finally the ``HivePlot.edges.edge_viz_kwargs``.

        If any keyword arguments in the ``hive_plot_edges`` attribute are also provided in this function's
        ``contours_kwargs``, then a warning will be raised.

        Hover information can only be generated for all edges at once in holoviews with the ``bokeh`` backend, so hover
        information fields will be dictated by a single tag of data even if different data tags have different dataframe
        columns.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param hover: whether to add hover information or not for edges. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs. Hover information will be generated as a function of a
        single tag of data, even if multiple tags are plotted (see note above for more details).
    :param contours_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified
        beforehand in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` / :py:meth:`hiveplotlib.P2CP.build_edges` or
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` / :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will take
        priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` /
        :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `holoviews.Contours() <https://holoviews.org/reference/elements/bokeh/Contours.html>`__ call. Edge data values
        can also be used, see note above for more details.
    :raises ValueError: if user tries to use the ``"line_color"`` parameter with the ``holoviews-bokeh`` back end (only
        ``"color"`` can be used to set the edge color with the ``bokeh`` back end).
    :return: ``holoviews.Overlay``.
    """
    backend = _get_current_hv_backend()

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="edges")

    # stop plotting if there are no edges to plot
    if warning_raised:
        return None

    if backend == "bokeh":
        line_width_name = "line_width"
    elif backend == "matplotlib":
        line_width_name = "linewidth"

    # p2cp warnings only need to happen once per tag
    #  because all axes behave in unison
    already_warned_p2cp_tags = []

    edges_plots = []

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
                temp_edge_kwargs, already_warned_p2cp_tags = edge_viz_preparation(
                    hive_plot=hive_plot,
                    name=name,
                    from_axis=a0,
                    to_axis=a1,
                    tag=tag,
                    already_warned_p2cp_tags=already_warned_p2cp_tags,
                    edge_kwargs=contours_kwargs,
                    line_width_name=line_width_name,
                    line_alpha_name="alpha",
                    line_color_name="color",
                )

                # store data-specific kwargs separately
                data_kwargs = {}
                # data kwargs specifically for viz, not just metadata
                data_viz_kwargs = {}

                # add to / overwrite any provided edge kwargs with the Edges ``edge_viz_kwargs``
                # propagating column names as the column names because bokeh infers the data on its own
                if hive_plot.edges is not None:
                    # store all the metadata in data_kwargs no matter what
                    relevant_edges = hive_plot.edges.relevant_edges[a0][a1][tag]
                    relevant_df = hive_plot.edges._data[tag].loc[relevant_edges, :]
                    data_kwargs |= relevant_df.to_dict(orient="list")

                    # priority queue of edge kwargs
                    final_edge_kwargs = (
                        hive_plot.edges.edge_viz_kwargs[tag]
                        | temp_edge_kwargs.copy()
                        | hive_plot.hive_plot_edges[a0][a1][tag]["edge_kwargs"]
                    )
                    if backend == "bokeh" and "line_color" in final_edge_kwargs:
                        raise ValueError(
                            "Hiveplotlib does not support using the 'line_color' parameter"
                            " with the `holoviews-bokeh` backend. "
                            "Please switch to using the 'color' parameter instead.",
                        )
                    # if any kwarg value corresponds to an edge data column name, use the edge data values
                    keys_vals = final_edge_kwargs.copy().items()
                    for kw, val in keys_vals:
                        # if value is name of column, then propagate those values as a 1d array (e.g. value per edge)
                        if (
                            isinstance(val, Hashable)
                            and val in hive_plot.edges._data[tag].columns
                        ):
                            # pass the data-based kwargs to a separate dict for insertion into arrays later
                            data_viz_kwargs[kw] = val
                            # drop key from edge kwargs, we will add manually later as a dim()
                            del final_edge_kwargs[kw]
                        # otherwise pass on the kwarg normally
                        else:
                            final_edge_kwargs[kw] = val
                else:
                    final_edge_kwargs = temp_edge_kwargs.copy()
                    # add any hive plot edge kwargs (if existing)
                    if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                        final_edge_kwargs |= hive_plot.hive_plot_edges[a0][a1][tag][
                            "edge_kwargs"
                        ]

                # only run plotting of edges that exist
                if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                    # grab the requested array of discretized curves
                    edge_arr = hive_plot.hive_plot_edges[a0][a1][tag]["curves"]
                    # if there's no actual edges there, don't plot
                    if edge_arr.size > 0:
                        split_arrays = np.split(
                            edge_arr, np.where(np.isnan(edge_arr[:, 0]))[0]
                        )[:-1]  # last element is a [NaN, NaN] array
                        xs = [arr[:, 0] for arr in split_arrays]
                        ys = [arr[:, 1] for arr in split_arrays]
                        # get one dict per curve of data variable informatiion
                        data_dicts = [
                            {a: data_kwargs[a][i] for a in data_kwargs}
                            for i, _ in enumerate(split_arrays)
                        ]
                        contours = [
                            {"x": x, "y": y, **data_dict}
                            for (x, y, data_dict) in zip(xs, ys, data_dicts)
                        ]

                        # HACK: solution to https://github.com/holoviz/holoviews/issues/6469 for the moment
                        # TODO: revisit after holoviews>=1.22 release
                        if (
                            "color" not in data_viz_kwargs and backend == "bokeh"
                        ):  # when color is a single color, not data-based
                            # Contours() call uses one of the vdims for color without our consent
                            # hack is to make cmap the single color we intended to use
                            final_edge_kwargs["cmap"] = [final_edge_kwargs["color"]]

                        final_edge_kwargs["show_legend"] = (
                            False  # default legend that shows up not informative here
                        )
                        temp_curves = hv.Contours(
                            contours,
                            kdims=["x", "y"],
                            vdims=list(data_kwargs.keys()),
                            group="edges",
                            label=f"{tag}",  # tag labels must be strings
                        ).opts(
                            **final_edge_kwargs,
                            **{
                                val: dim(data_viz_kwargs[val])
                                for val in data_viz_kwargs
                            },
                        )
                        edges_plots.append(temp_curves)

    edges_fig = hv.Overlay(edges_plots)

    if hover is True and backend == "bokeh":
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        elif len(edges_plots) > 0 and hive_plot.edges is not None:
            variables = [
                f"<div>{i}: @{{{i}}}</div>"
                if i
                not in [
                    hive_plot.edges.from_column_name,
                    hive_plot.edges.to_column_name,
                ]
                else ""
                for i in hive_plot.edges._data[list(tags_to_plot)[0]].columns
            ]
            right_arrow = "&#x27A1;"
            tooltips = f"""
            <div>
                <b>Edge: @{{{hive_plot.edges.from_column_name}}} {right_arrow} @{{{hive_plot.edges.to_column_name}}}</b>
                {"".join(variables)}
            </div>
            """
            hover_tool = HoverTool(
                tooltips=tooltips,
                description="Edge Hover Info",
                renderers=[hv.render(i).renderers[0] for i in edges_plots],
            )
            edges_fig.opts(hv.opts.Contours(tools=[hover_tool]))

    # compose with existing fig if one was provided
    final_fig = fig * edges_fig if fig is not None else edges_fig

    # holoviews modification comes at the end because we modify *existing* figures with .opts()
    return _holoviews_fig_modification(
        hive_plot=hive_plot,
        fig=final_fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
    )


def hive_plot_viz(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[hv.Overlay] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    text_kwargs: Optional[dict] = None,
    overlay_kwargs: Optional[dict] = None,
    hover: Union[
        bool,
        Literal["nodes", "edges", "axes"],
        list[Literal["nodes", "edges", "axes"],],
    ] = True,
    **edge_kwargs,
) -> hv.Overlay:
    """
    Create default ``holoviews`` visualization of a ``HivePlot`` instance.

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

        When including edge hover information, this can only be generated for all edges at once in holoviews with the
        ``bokeh`` backend, so hover information fields will be dictated by a single tag of data even if different data
        tags have different dataframe columns.

        When including axis hover information, and a subset of axes has metadata not available on other axes, all axes
        will show that metadata variable, but the axes without the variable will display the value N/A.

    :param hive_plot: ``HivePlot`` instance we want to visualize.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
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
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param node_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `holoviews.Points() <https://holoviews.org/reference/elements/matplotlib/Points.html>`__ call.
        Node data values can also be used, see note above for more details.
    :param axes_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a `holoviews.Segments() <https://holoviews.org/reference/elements/bokeh/Segments.html>`__ call.
    :param text_kwargs: additional kwargs passed to
        `holoviews.Text() <https://holoviews.org/reference/elements/bokeh/Text.html>`__ call.
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param hover: whether to add hover information or not for nodes, edges, and / or axes. ``False`` excludes all hover
        information, while default ``True`` includes node, edge, and axis hover information. Providing the value
        ``"nodes"`` / ``"edges"`` / ``"axes"`` adds hover information ONLY for nodes / edges / axes. Users can also
        provide a list of a subset of these values (e.g. providing ``["nodes", "edges"]`` would show all hover info
        except for axes).
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified
        beforehand in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` or
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` will take priority). To overwrite previously set kwargs,
        see :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `holoviews.Contours() <https://holoviews.org/reference/elements/bokeh/Contours.html>`__ call. Edge data values
        can also be used, see note above for more details.
    :raises ValueError: if user tries to use the ``"line_color"`` parameter with the ``holoviews-bokeh`` back end (only
        ``"color"`` can be used to set the edge color with the ``bokeh`` back end).
    :return: ``holoviews.Overlay``.
    """
    hover_input_check(hover=hover)

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
        tags=tags,
        center_plot=False,
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

    fig = axes_viz(
        instance=hive_plot,
        fig=fig,
        center_plot=False,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        text_kwargs=text_kwargs,
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
    return node_viz(
        instance=hive_plot,
        fig=fig,
        width=width,
        height=height,
        buffer=buffer,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
        **node_hover_kwargs,
        **node_kwargs,
    )


def p2cp_viz(
    p2cp: P2CP,
    fig: Optional[hv.Overlay] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    text_kwargs: Optional[dict] = None,
    overlay_kwargs: Optional[dict] = None,
    **edge_kwargs,
) -> hv.Overlay:
    """
    Create default ``holoviews`` visualization of a ``P2CP`` instance.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: default ``None`` builds new overlay. If an overlay is specified, axes will be drawn on that overlay.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure. When the ``holoviews`` backend is set to ``"bokeh"``, width must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, width must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure. When the ``holoviews`` backend is set to ``"bokeh"``, height must be specified in
        *pixels*, defaulting to 600. When the ``holoviews`` backend is set to ``"matplotlib"``, height must be specified
        in *inches*, defaulting to 10. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
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
    :param axes_off: whether to turn off Cartesian x, y axes in the ``hv.Overlay`` (default ``True`` hides the x and y
        axes).
    :param node_kwargs: additional params that will be applied to all P2CP nodes. Note, these are kwargs that
        affect a `holoviews.Points() <https://holoviews.org/reference/elements/matplotlib/Points.html>`__ call.
    :param axes_kwargs: additional params that will be applied to all P2CP axes. Note, these are kwargs that
        affect a `holoviews.Segments() <https://holoviews.org/reference/elements/bokeh/Segments.html>`__ call.
    :param text_kwargs: additional kwargs passed to
        `holoviews.Text() <https://holoviews.org/reference/elements/bokeh/Text.html>`__ call.
    :param overlay_kwargs: additional values to be called in ``hv.Overlay().opts()`` call. Note if ``width`` and
        ``height`` are added here, then they will be prioritized over the ``width`` and ``height`` parameters.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.P2CP.build_edges()` or :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will
        take priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more.
        Note, these are kwargs that affect a
        `holoviews.Contours() <https://holoviews.org/reference/elements/bokeh/Contours.html>`__ call.
    :return: ``holoviews.Overlay``.
    """
    if node_kwargs is None:
        node_kwargs = {}

    if axes_kwargs is None:
        axes_kwargs = {}

    if "hover" in edge_kwargs:
        del edge_kwargs["hover"]
        if _get_current_hv_backend() == "bokeh":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )

    fig = edge_viz(
        instance=p2cp,
        fig=fig,
        tags=tags,
        center_plot=False,
        hover=False,  # hover not currently supported for P2CPs
        **edge_kwargs,
    )

    fig = axes_viz(
        instance=p2cp,
        fig=fig,
        center_plot=False,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        text_kwargs=text_kwargs,
        hover=False,  # hover not currently supported for P2CPs
        **axes_kwargs,
    )

    # do the centering / redim-ing if requested only on the last call, otherwise it will be overridden
    return node_viz(
        instance=p2cp,
        fig=fig,
        width=width,
        height=height,
        buffer=buffer,
        center_plot=center_plot,
        axes_off=axes_off,
        overlay_kwargs=overlay_kwargs,
        hover=False,  # hover not currently supported for P2CPs
        **node_kwargs,
    )


def p2cp_legend(
    fig: hv.Overlay,
    **legend_kwargs,
) -> hv.Overlay:
    """
    Generate a legend for a ``P2CP`` instance, where entries in the legend will be tags of data added to the instance.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: ``plotly`` figure on which we will draw the legend.
    :param legend_kwargs: additional values to be called in ``hv.Overlay().opts()`` call.
    :return: ``holoviews.Overlay``.
    """
    return fig.opts(hv.opts.Contours(show_legend=True), **legend_kwargs)
