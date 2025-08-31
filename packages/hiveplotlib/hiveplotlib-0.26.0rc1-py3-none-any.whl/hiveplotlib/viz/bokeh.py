# bokeh.py

"""
``bokeh``-backend visualizations in ``hiveplotlib``.
"""

try:
    from bokeh.models import ColumnDataSource, Label, Range1d
    from bokeh.plotting import figure
except ImportError as ie:  # pragma: no cover
    raise ImportError(
        "bokeh not installed, but can be installed by running `pip install hiveplotlib[bokeh]`"
    ) from ie

import warnings
from typing import Hashable, List, Literal, Optional, Union

import numpy as np
import pandas as pd
from bokeh.models import HoverTool

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


def _bokeh_fig_setup(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[figure] = None,
    buffer: float = 0.3,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
) -> figure:
    """
    Set up ``bokeh`` figure and perform any further adjustments based on other parameter settings.

    :param hive_plot: ``HivePlot`` instance to plot. Should never take a ``P2CP`` instance.
    :param fig: figure to modify, generates one if ``None`` provided.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True`` hides the
        x and y axes).
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :return: resulting ``bokeh`` figure.
    """
    if fig_kwargs is None:
        fig_kwargs = {}

    # allow for plotting onto specified figure
    if fig is None:
        fig_kwargs.setdefault("height", height)
        fig_kwargs.setdefault("width", width)
        fig = figure(**fig_kwargs)

    # can only center the plot if you have axes
    if center_plot and hive_plot.max_polar_end is not None:
        # center plot at (0, 0)
        max_radius = hive_plot.max_polar_end
        # throw in a minor buffer
        buffer_radius = buffer * max_radius
        max_radius += buffer_radius

        fig.x_range = Range1d(-max_radius, max_radius)
        fig.y_range = Range1d(-max_radius, max_radius)

    if axes_off:
        fig.axis.visible = False
        fig.grid.visible = False
        fig.outline_line_color = None
    else:
        fig.axis.visible = True
        fig.grid.visible = True
        fig.outline_line_color = "#e5e5e5"

    return fig


def axes_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[figure] = None,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: str = "16px",
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    hover: bool = True,
    label_kwargs: Optional[dict] = None,
    **line_kwargs,
) -> figure:
    """
    ``bokeh`` visualization of axes in a ``HivePlot`` or ``P2CP`` instance.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw axes.
    :param fig: default ``None`` builds new figure. If a figure is specified, axes will be drawn on that figure.
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
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param hover: whether to add hover information or not for axes. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param label_kwargs: additional kwargs passed to
        `bokeh.models.Label() <https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Label>`__
        call.
    :param line_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a `bokeh.models.Line() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html>`__ call.
    :return: ``bokeh`` figure.
    """
    # some default kwargs for the axes
    line_kwargs.setdefault("color", "black")
    line_kwargs.setdefault("line_alpha", 0.5)
    line_kwargs.setdefault("line_width", 1.5)

    metadata_variables_to_exclude = ["long_name", "x", "y"]

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    if label_kwargs is None:
        label_kwargs = {}

    fig = _bokeh_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    line_outputs = []

    # compile all axis metadata variables to be used in hover tooltips first
    axis_metadata_variables = set()
    for axis in hive_plot.axes.values():
        df = get_hover_axis_metadata(axis=axis)

        # track all possible metadata variables
        metadata_variables = {
            i for i in df.columns if i not in metadata_variables_to_exclude
        }
        axis_metadata_variables = axis_metadata_variables.union(metadata_variables)

    for axis in hive_plot.axes.values():
        to_plot = np.vstack((axis.start, axis.end))
        df = get_hover_axis_metadata(axis=axis)
        missing_cols = axis_metadata_variables.difference(set(df.columns))
        # fill in missing columns with "N/A" string for hover tooltips
        for col in missing_cols:
            df[col] = "N/A"
        df["x"] = to_plot[:, 0]
        df["y"] = to_plot[:, 1]
        # make sure names are always hover compatible
        df, original_to_sanitized_map = __sanitize_dataframe_columns(df)
        data = ColumnDataSource(data=df)
        line = fig.line(
            x=original_to_sanitized_map["x"],
            y=original_to_sanitized_map["y"],
            source=data,
            **line_kwargs,
        )
        line_outputs.append(line)

    if show_axes_labels:
        label_axes(
            instance=hive_plot,
            fig=fig,
            center_plot=False,
            axes_labels_buffer=axes_labels_buffer,
            axes_labels_fontsize=axes_labels_fontsize,
            axes_off=axes_off,
            **label_kwargs,
        )

    if hover is True and len(line_outputs) > 0:
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
            fig.add_tools(
                HoverTool(
                    tooltips=tooltips,
                    description="Axis Hover Info",
                    renderers=line_outputs,
                    attachment="vertical",
                    anchor="bottom_right",
                )
            )

    return fig


def label_axes(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[figure] = None,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: str = "16px",
    buffer: float = 0.3,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    **label_kwargs,
) -> figure:
    """
    ``bokeh`` visualization of axis labels in a ``HivePlot`` or ``P2CP`` instance.

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
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param label_kwargs: additional kwargs passed to
        `bokeh.models.Label() <https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Label>`__
        call.
    :return: ``bokeh`` figure.
    """
    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    fig = _bokeh_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    for axis in hive_plot.axes.values():
        # choose horizontal and vertical alignment based on axis angle in [0, 360)
        vertical_alignment, horizontal_alignment = get_axis_label_alignment(
            axis=axis,
            backend="bokeh",
        )

        x, y = polar2cartesian(axes_labels_buffer * axis.polar_end, axis.angle)
        label = Label(
            x=x,
            y=y,
            text=axis.long_name,
            text_font_size=axes_labels_fontsize,
            text_align=horizontal_alignment,
            text_baseline=vertical_alignment,
            **label_kwargs,
        )
        fig.add_layout(label)

    return fig


def node_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[figure] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    hover: bool = True,
    **scatter_kwargs,
) -> figure:
    """
    ``bokeh`` visualization of nodes in a ``HivePlot`` or ``P2CP`` instance that have been placed on their axes.

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
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param hover: whether to add hover information or not for nodes. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs.
    :param scatter_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `fig.scatter() <https://docs.bokeh.org/en/latest/docs/reference/plotting/figure.html#bokeh.plotting.figure.scatter>`__
        call. Node data values can also be used, see note above for more details.
    :return: ``bokeh`` figure.
    """
    # some default kwargs for the nodes
    scatter_kwargs.setdefault("color", "black")
    scatter_kwargs.setdefault("alpha", 0.8)
    scatter_kwargs.setdefault("size", 5)

    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="nodes")

    fig = _bokeh_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    # stop plotting if there are no nodes to plot
    if warning_raised:
        return fig

    # add to / overwrite any provided scatter kwargs with the NodeCollection ``node_viz_kwargs``
    # propagating column names as the column names because bokeh infers the data on its own
    final_scatter_kwargs = scatter_kwargs.copy() | hive_plot.nodes.node_viz_kwargs
    scatter_outputs = []
    for axis in hive_plot.axes.values():
        df_to_plot = axis.node_placements.drop(columns=["rho"])
        to_plot = ColumnDataSource(df_to_plot)
        if df_to_plot.shape[0] > 0:
            scatter = fig.scatter("x", "y", source=to_plot, **final_scatter_kwargs)
            scatter_outputs.append(scatter)

    if hover is True:
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        elif len(scatter_outputs) > 0:
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
            fig.add_tools(
                HoverTool(
                    tooltips=tooltips,
                    description="Node Hover Info",
                    renderers=scatter_outputs,
                    attachment="horizontal",
                    anchor="top_left",
                )
            )

    return fig


def edge_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    hover: bool = True,
    **edge_kwargs,
) -> figure:
    """
    ``bokeh`` visualization of constructed edges in a ``HivePlot`` or ``P2CP`` instance.

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

        Hover information can only be generated for all edges at once with the ``bokeh`` backend, so hover
        information fields will be dictated by a single tag of data even if different data tags have different dataframe
        columns.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param fig: default ``None`` builds new figure. If a figure is specified, edges will be drawn on that figure.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param width: width of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param height: height of figure in pixels. Note: only works if instantiating new figure (e.g. ``fig`` is ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param hover: whether to add hover information or not for edges. ``False`` excludes hover information. Default
        ``True``. Only works currently for Hive Plots, not P2CPs. Hover information will be generated as a function of a
        single tag of data, even if multiple tags are plotted (see note above for more details).
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` / :py:meth:`hiveplotlib.P2CP.build_edges` or
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` / :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will take
        priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` /
        :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `bokeh.models.MultiLine() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/multi_line.html>`__
        call. Edge data values can also be used, see note above for more details.
    :return: ``bokeh`` figure.
    """
    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="edges")

    fig = _bokeh_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        buffer=buffer,
        width=width,
        height=height,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    # stop plotting if there are no edges to plot
    if warning_raised:
        return fig

    # p2cp warnings only need to happen once per tag
    #  because all axes behave in unison
    already_warned_p2cp_tags = []

    line_outputs = []

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
                    edge_kwargs=edge_kwargs,
                    line_width_name="line_width",
                    line_alpha_name="alpha",
                    line_color_name="color",
                )

                # add to / overwrite any provided edge kwargs with the Edges ``edge_viz_kwargs``
                # propagating column names as the column names because bokeh infers the data on its own
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
                        cds_data = {"xs": xs, "ys": ys}
                        if hive_plot.edges is not None:
                            relevant_edges = hive_plot.edges.relevant_edges[a0][a1][tag]
                            relevant_df = hive_plot.edges._data[tag][relevant_edges]
                            cds_data |= relevant_df.to_dict(orient="list")
                        source = ColumnDataSource(cds_data)
                        # add legend labels but then remove them to not plot unless legend formally called later
                        line = fig.multi_line(
                            xs="xs",
                            ys="ys",
                            source=source,
                            legend_label=str(tag),
                            **final_edge_kwargs,
                        )
                        line_outputs.append(line)
    if hover is True:
        if name == "P2CP":
            warnings.warn(
                "Hover info not yet supported for P2CPs, disregarding 'hover' parameter...",
                stacklevel=2,
            )
        elif len(line_outputs) > 0 and hive_plot.edges is not None:
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
            fig.add_tools(
                HoverTool(
                    tooltips=tooltips,
                    description="Edge Hover Info",
                    renderers=line_outputs,
                )
            )

    # kill all legend labeling for initial rendering (if there is anything that plotted with labels)
    if fig.legend != []:
        for i in fig.legend.items:
            i.visible = False

    return fig


def hive_plot_viz(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: str = "16px",
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    label_kwargs: Optional[dict] = None,
    fig_kwargs: Optional[dict] = None,
    hover: Union[
        bool,
        Literal["nodes", "edges", "axes"],
        list[Literal["nodes", "edges", "axes"],],
    ] = True,
    **edge_kwargs,
) -> figure:
    """
    Create default ``bokeh`` visualization of a ``HivePlot`` instance.

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

        When including edge hover information, this can only be generated for all edges at once with the ``bokeh`` back
        end, so hover information fields will be dictated by a single tag of data even if different data tags have
        different dataframe columns.

        When including axis hover information, and a subset of axes has metadata not available on other axes, all axes
        will show that metadata variable, but the axes without the variable will display the value N/A.

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
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a `fig.scatter() <https://docs.bokeh.org/en/latest/docs/reference/plotting/figure.html#bokeh.plotting.figure.scatter>`_
        call. Node data values can also be used, see note above for more details.
    :param axes_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a `bokeh.models.Line() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html>`__ call.
    :param label_kwargs: additional kwargs passed to
        `bokeh.models.Label() <https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Label>`__
        call.
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param hover: whether to add hover information or not for nodes, edges, and / or axes. ``False`` excludes all hover
        information, while default ``True`` includes node, edge, and axis hover information. Providing the value
        ``"nodes"`` / ``"edges"`` / ``"axes"`` adds hover information ONLY for nodes / edges / axes. Users can also
        provide a list of a subset of these values (e.g. providing ``["nodes", "edges"]`` would show all hover info
        except for axes).
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` or :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()`
        will take priority). To overwrite previously set kwargs, see
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        `bokeh.models.MultiLine() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/multi_line.html>`__
        call. Edge data values can also be used, see note above for more details.
    :raises InvalidHoverVariableError: if invalid input provided to ``hover`` parameter.
    :return: ``bokeh`` figure.
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
        width=width,
        height=height,
        tags=tags,
        center_plot=False,
        fig_kwargs=fig_kwargs,
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
    fig: Optional[figure] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    width: int = 600,
    height: int = 600,
    center_plot: bool = True,
    buffer: float = 0.3,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: str = "16px",
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    label_kwargs: Optional[dict] = None,
    fig_kwargs: Optional[dict] = None,
    **edge_kwargs,
) -> figure:
    """
    Create default ``bokeh`` visualization of a ``P2CP`` instance.

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
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``bokeh`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all P2CP nodes. Note, these are kwargs that
        affect a `fig.scatter() <https://docs.bokeh.org/en/latest/docs/reference/plotting/figure.html#bokeh.plotting.figure.scatter>`__
        call.
    :param axes_kwargs: additional params that will be applied to all P2CP axes. Note, these are kwargs that
        affect a `bokeh.models.Line() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html>`__ call.
    :param label_kwargs: additional kwargs passed to
        `bokeh.models.Label() <https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Label>`__
        call.
    :param fig_kwargs: additional values to be called in
        `bokeh.plotting.figure() <https://docs.bokeh.org/en/2.4.1/docs/reference/plotting/figure.html>`__ call. Note if
        ``width`` and ``height`` are added here, then they will be prioritized over the ``width`` and ``height``
        parameters.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.P2CP.build_edges()` or :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will
        take priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more.
        Note, these are kwargs that affect a
        `bokeh.models.MultiLine() <https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/multi_line.html>`__
        call.
    :return: ``bokeh`` figure.
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
        fig_kwargs=fig_kwargs,
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
    fig: figure,
    tags: Optional[Union[List[Hashable], Hashable]] = None,
    title: str = "Tags",
) -> figure:
    """
    Generate a legend for a ``P2CP`` instance, where entries in the legend will be tags of data added to the instance.

    .. note::
        The legend can be further modified by changing its attributes under ``fig.legend``. For more on the flexibility
        in changing the legend, see the
        `bokeh.models.Legend() <https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Legend>`__
        docs.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: ``bokeh`` figure on which we will draw the legend.
    :param tags: which tags of data to include in the legend. Default ``None`` uses all tags under
        ``p2cp.tags``. This can be ignored unless explicitly wanting to *exclude* certain tags from the legend.
    :param title: title of the legend. Default "Tags".
    :return: ``bokeh`` figure.
    """
    # kill all legend labeling before rebuilding legend
    for i in fig.legend.items:
        i.visible = False

    # need to convert tags to strings, as we needed to coax to strings to make them legend values with bokeh
    tags = (
        [str(i) for i in p2cp.tags[:]]
        if tags is None
        else list(np.array(tags).flatten().astype(str))
    )

    for i in fig.legend.items:
        if str(i.label["value"]) in tags:
            i.visible = True

    fig.legend.title = title

    return fig
