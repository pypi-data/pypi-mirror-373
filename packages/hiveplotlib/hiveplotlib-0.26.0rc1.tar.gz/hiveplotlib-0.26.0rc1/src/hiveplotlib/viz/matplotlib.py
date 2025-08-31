# matplotlib.py

"""
``matplotlib``-backend visualizations in ``hiveplotlib``.
"""

from typing import Hashable, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

from hiveplotlib import P2CP, BaseHivePlot, HivePlot
from hiveplotlib.utils import polar2cartesian
from hiveplotlib.viz.base import edge_viz_preparation, get_axis_label_alignment
from hiveplotlib.viz.input_checks import input_check


def _matplotlib_fig_setup(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    buffer: float = 0.1,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Set up ``matplotlib`` figure and perform any further adjustments based on other parameter settings.

    :param hive_plot: ``HivePlot`` instance to plot. Should never take a ``P2CP`` instance.
    :param fig: default ``None`` builds new figure. If a figure is specified, axes will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, ``Axis`` instances will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :return: resulting ``plotly`` figure.
    """
    if fig_kwargs is None:
        fig_kwargs = {}

    fig_kwargs.setdefault("figsize", figsize)

    # allow for plotting onto specified figure, axis
    if fig is None and ax is None:
        fig, ax = plt.subplots(**fig_kwargs)

    if center_plot and hive_plot.max_polar_end is not None:
        ax.axis("equal")
        # center plot at (0, 0)
        max_radius = hive_plot.max_polar_end
        # throw in a minor buffer
        buffer_radius = buffer * max_radius
        max_radius += buffer_radius
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)

    if axes_off:
        ax.axis("off")
    else:
        ax.axis("on")

    return fig, ax


def axes_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    buffer: float = 0.1,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    text_kwargs: Optional[dict] = None,
    **axes_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of axes in a ``HivePlot`` or ``P2CP`` instance.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw axes.
    :param fig: default ``None`` builds new figure. If a figure is specified, axes will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, ``Axis`` instances will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param text_kwargs: additional kwargs passed to ``plt.text()`` call.
    :param axes_kwargs: additional params that will be applied to all hive plot axes. Note, these are kwargs that
        affect a ``plt.plot()`` call.
    :return: ``matplotlib`` figure, axis.
    """
    # some default kwargs for the axes
    if "c" not in axes_kwargs and "color" not in axes_kwargs:
        axes_kwargs["c"] = "black"
    axes_kwargs.setdefault("alpha", 0.5)

    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="axes")

    fig, ax = _matplotlib_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        ax=ax,
        buffer=buffer,
        figsize=figsize,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    if warning_raised:
        return fig, ax

    if text_kwargs is None:
        text_kwargs = {}

    for axis in hive_plot.axes:
        to_plot = np.vstack((hive_plot.axes[axis].start, hive_plot.axes[axis].end))
        ax.plot(to_plot[:, 0], to_plot[:, 1], **axes_kwargs)

    if show_axes_labels:
        label_axes(
            instance=hive_plot,
            fig=fig,
            ax=ax,
            center_plot=False,
            axes_labels_buffer=axes_labels_buffer,
            axes_labels_fontsize=axes_labels_fontsize,
            axes_off=axes_off,
            **text_kwargs,
        )
    return fig, ax


def label_axes(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    buffer: float = 0.1,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    **text_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of axis labels in a ``HivePlot`` or ``P2CP`` instance.

    For ``HivePlot`` instances, each axis' ``long_name`` attribute will be used. For ``P2CP`` instances, column names in
    the ``data`` attribute will be used.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw nodes.
    :param fig: default ``None`` builds new figure. If a figure is specified, axis labels will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, axis labels will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for axes labels.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param text_kwargs: additional kwargs passed to ``plt.text()`` call.
    :return: ``matplotlib`` figure, axis.
    """
    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="axes")

    if warning_raised:
        return None

    fig, ax = _matplotlib_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        ax=ax,
        buffer=buffer,
        figsize=figsize,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    for axis in hive_plot.axes.values():
        # choose horizontal and vertical alignment based on axis angle in [0, 360)
        vertical_alignment, horizontal_alignment = get_axis_label_alignment(
            axis=axis,
            backend="matplotlib",
        )

        x, y = polar2cartesian(axes_labels_buffer * axis.polar_end, axis.angle)
        ax.text(
            x,
            y,
            axis.long_name,
            fontsize=axes_labels_fontsize,
            horizontalalignment=horizontal_alignment,
            verticalalignment=vertical_alignment,
            **text_kwargs,
        )

    return fig, ax


def node_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    buffer: float = 0.1,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    **scatter_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of nodes in a ``HivePlot`` or ``P2CP`` instance that have been placed on its axes.

    .. note::
        If ``instance`` is a ``HivePlot``, then users can provide node-specific data to plotting keyword arguments by
        providing column names from the ``HivePlot.nodes.data`` DataFrame as values in either the
        ``HivePlot.nodes.node_viz_kwargs`` dictionary via ``HivePlot.update_node_viz_kwargs()`` or in this call in the
        provided ``scatter_kwargs``.

        If ``instance`` is a ``HivePlot``, then any provided node plotting keyword arguments in
        ``HivePlot.nodes.node_viz_kwargs`` will be prioritized over any provided ``scatter_kwargs``.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw nodes.
    :param fig: default ``None`` builds new figure. If a figure is specified, nodes will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, `nodes will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param scatter_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a ``plt.scatter()`` call. Node data values can also be used, see note above for more details.
    :return: ``matplotlib`` figure, axis.
    """
    # some default kwargs for the nodes
    if (
        "c" not in scatter_kwargs
        and "color" not in scatter_kwargs
        and "facecolor" not in scatter_kwargs
    ):
        scatter_kwargs["c"] = "black"
    scatter_kwargs.setdefault("alpha", 0.8)
    scatter_kwargs.setdefault("s", 20)

    hive_plot, _, _ = input_check(instance, objects_to_plot="nodes")

    fig, ax = _matplotlib_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        ax=ax,
        buffer=buffer,
        figsize=figsize,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
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
        # drop default "c" color if user provided color another way
        if (
            "color" in final_scatter_kwargs or "facecolor" in final_scatter_kwargs
        ) and "c" in final_scatter_kwargs:
            del final_scatter_kwargs["c"]
        to_plot = axis.node_placements.loc[:, ["x", "y"]].to_numpy()[:, :2]
        if to_plot.shape[0] > 0:
            ax.scatter(to_plot[:, 0], to_plot[:, 1], **final_scatter_kwargs)

    return fig, ax


def edge_viz(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    buffer: float = 0.1,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    prioritize_array_over_color: bool = True,
    **edge_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of constructed edges in a ``HivePlot`` or ``P2CP`` instance.

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

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param fig: default ``None`` builds new figure. If a figure is specified, edges will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, edges will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``instance``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param prioritize_array_over_color: if both ``array`` and ``color`` are provided by the user as edge kwargs for any
        subset of edges, then setting this to ``True`` will drop ``color`` and use ``array`` to color edges. If
        ``False``, will instead use ``color``. Default ``True``.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` / :py:meth:`hiveplotlib.P2CP.build_edges` or
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` / :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will take
        priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` /
        :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        ``matplotlib.collections.LineCollection()`` call. Edge data values can also be used, see note above for more
        details.
    :return: ``matplotlib`` figure, axis.
    """
    hive_plot, name, warning_raised = input_check(instance, objects_to_plot="edges")

    # stop plotting if there are no edges to plot
    if warning_raised:
        return None

    fig, ax = _matplotlib_fig_setup(
        hive_plot=hive_plot,
        fig=fig,
        ax=ax,
        buffer=buffer,
        figsize=figsize,
        center_plot=center_plot,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
    )

    # p2cp warnings only need to happen once per tag
    #  because all axes behave in unison
    already_warned_p2cp_tags = []

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
                    line_width_name="linewidth",
                    line_alpha_name="alpha",
                    line_color_name="color",
                    include_line_color=False,
                    include_line_width=False,
                )
                # add to / overwrite any provided edge kwargs with the appropriate ``edge_viz_kwargs``
                if hive_plot.edges is not None:
                    # priority queue of edge kwargs
                    final_edge_kwargs = (
                        hive_plot.edges.edge_viz_kwargs[tag]
                        | temp_edge_kwargs.copy()
                        | hive_plot.hive_plot_edges[a0][a1][tag]["edge_kwargs"]
                    )
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
                else:
                    final_edge_kwargs = temp_edge_kwargs.copy()
                    # add any hive plot edge kwargs (if existing)
                    if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                        final_edge_kwargs |= hive_plot.hive_plot_edges[a0][a1][tag][
                            "edge_kwargs"
                        ]

                if "array" in final_edge_kwargs and "color" in final_edge_kwargs:
                    if prioritize_array_over_color:
                        del final_edge_kwargs["color"]
                    else:
                        del final_edge_kwargs["array"]
                # matplotlib-specific case control, if user wants to color edges by a parameter,
                #  and they provide the ``array`` kwarg but not ``color``
                #  if they provided neither, then we put default color black in here
                if (
                    "color" not in final_edge_kwargs
                    and "array" not in final_edge_kwargs
                ):
                    final_edge_kwargs["color"] = "black"
                # only run plotting of edges that exist
                if "curves" in hive_plot.hive_plot_edges[a0][a1][tag]:
                    # grab the requested array of discretized curves
                    edge_arr = hive_plot.hive_plot_edges[a0][a1][tag]["curves"]
                    # if there's no actual edges there, don't plot
                    if edge_arr.size > 0:
                        split_arrays = np.split(
                            edge_arr, np.where(np.isnan(edge_arr[:, 0]))[0]
                        )[:-1]  # last element is a [NaN, NaN] array
                        collection = LineCollection(
                            split_arrays,
                            **final_edge_kwargs,
                        )
                        ax.add_collection(collection)

    return fig, ax


def hive_plot_viz(
    hive_plot: Union[BaseHivePlot, HivePlot],
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    buffer: float = 0.1,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    text_kwargs: Optional[dict] = None,
    fig_kwargs: Optional[dict] = None,
    prioritize_array_over_color: bool = True,
    **edge_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of a ``HivePlot`` instance.

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

    :param hive_plot: ``HivePlot`` instance we want to visualize.
    :param fig: default ``None`` builds new figure. If a figure is specified, hive plot will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, hive plot will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``hive_plot``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for hive plot axes labels.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all hive plot nodes. Note, these are kwargs that
        affect a ``plt.scatter()`` call. Node data values can also be used, see note above for more details.
    :param axes_kwargs: additional params that will be applied to all axes. Note, these are kwargs that affect
        a ``plt.plot()`` call.
    :param text_kwargs: additional kwargs passed to ``plt.text()`` call.
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param prioritize_array_over_color: if both ``array`` and ``color`` are provided by the user as edge kwargs for any
        subset of edges, then setting this to ``True`` will drop ``color`` and use ``array`` to color edges. If
        ``False``, will instead use ``color``. Default ``True``.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.BaseHivePlot.connect_axes()` or :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()`
        will take priority). To overwrite previously set kwargs, see
        :py:meth:`hiveplotlib.BaseHivePlot.add_edge_kwargs()` for more. Note, these are kwargs that affect a
        ``matplotlib.collections.LineCollection()`` call. Edge data values can also be used, see note above for more
        details.
    :return: ``matplotlib`` figure, axis.
    """
    if node_kwargs is None:
        node_kwargs = {}

    if axes_kwargs is None:
        axes_kwargs = {}
    if text_kwargs is None:
        text_kwargs = {}
    fig, ax = axes_viz(
        instance=hive_plot,
        fig=fig,
        ax=ax,
        figsize=figsize,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        fig_kwargs=fig_kwargs,
        text_kwargs=text_kwargs,
        zorder=5,
        **axes_kwargs,
    )
    node_viz(
        instance=hive_plot,
        fig=fig,
        ax=ax,
        zorder=5,
        **node_kwargs,
    )
    # do the centering / redim-ing if requested only on the last call, otherwise it will be overridden
    edge_viz(
        instance=hive_plot,
        fig=fig,
        ax=ax,
        tags=tags,
        center_plot=center_plot,
        buffer=buffer,
        axes_off=axes_off,
        prioritize_array_over_color=prioritize_array_over_color,
        **edge_kwargs,
    )

    return fig, ax


def p2cp_viz(
    p2cp: P2CP,
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    tags: Optional[Union[Hashable, List[Hashable]]] = None,
    figsize: Tuple[float, float] = (10, 10),
    center_plot: bool = True,
    buffer: float = 0.1,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    axes_off: bool = True,
    node_kwargs: Optional[dict] = None,
    axes_kwargs: Optional[dict] = None,
    fig_kwargs: Optional[dict] = None,
    **edge_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    ``matplotlib`` visualization of a ``P2CP`` instance.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: default ``None`` builds new figure. If a figure is specified, P2CP will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, P2CP will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param tags: which tag(s) of data to plot. Default ``None`` plots all tags of data. Can supply either a single tag
        or list of tags.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param center_plot: whether to center the figure on ``(0, 0)``, the currently fixed center that the axes are drawn
        around by default. Will only run if there is at least one axis in ``p2cp``.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the P2CP axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for P2CP axes labels.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param node_kwargs: additional params that will be applied to all points on axes. Note, these are kwargs that
        affect a ``plt.scatter()`` call.
    :param axes_kwargs: additional params that will be applied to all axes. Note, these are kwargs that affect
        a ``plt.plot()`` call.
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param edge_kwargs: additional params that will be applied to all edges on all axes (but kwargs specified beforehand
        in :py:meth:`hiveplotlib.P2CP.build_edges()` or :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` will
        take priority). To overwrite previously set kwargs, see :py:meth:`hiveplotlib.P2CP.add_edge_kwargs()` for more.
        Note, these are kwargs that affect a ``matplotlib.collections.LineCollection()`` call.
    :return: ``matplotlib`` figure, axis.
    """
    if node_kwargs is None:
        node_kwargs = {}

    if axes_kwargs is None:
        axes_kwargs = {}

    fig, ax = axes_viz(
        instance=p2cp,
        fig=fig,
        ax=ax,
        figsize=figsize,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        fig_kwargs=fig_kwargs,
        zorder=5,
        **axes_kwargs,
    )
    node_viz(
        instance=p2cp,
        fig=fig,
        ax=ax,
        zorder=5,
        **node_kwargs,
    )
    # do the centering / redim-ing if requested only on the last call, otherwise it will be overridden
    edge_viz(
        instance=p2cp,
        fig=fig,
        ax=ax,
        tags=tags,
        center_plot=center_plot,
        buffer=buffer,
        axes_off=axes_off,
        **edge_kwargs,
    )

    return fig, ax


def p2cp_legend(
    p2cp: P2CP,
    fig: plt.Figure,
    ax: plt.Axes,
    tags: Optional[Union[List[Hashable], Hashable]] = None,
    title: str = "Tags",
    line_kwargs: Optional[dict] = None,
    **legend_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Generate a legend for a ``P2CP`` instance, where entries in the legend will be tags of data added to the instance.

    :param p2cp: ``P2CP`` instance we want to visualize.
    :param fig: ``matplotlib`` figure on which we will draw the legend.
    :param ax: ``matplotlib`` axis on which we will draw the legend.
    :param tags: which tags of data to include in the legend. Default ``None`` uses all tags under
        ``p2cp.tags``. This can be ignored unless explicitly wanting to *exclude* certain tags from the legend.
    :param title: title of the legend. Default "Tags".
    :param line_kwargs: keyword arguments that will add to / overwrite _all_ of the legend line markers from the
        defaults used in the original ``P2CP`` instance plot. For example, if one plots a large number of lines with low
        ``alpha`` and / or a small ``lw``, one will likely want to include ``line_kwargs=dict(alpha=1, lw=2)`` so the
        representative lines in the legend are legible.
    :param legend_kwargs: additional params that will be applied to the legend. Note, these are kwargs that affect a
        ``plt.legend()`` call. Default is to plot the legend in the upper right, outside of the bounding box (e.g.
        ``loc="upper left", bbox_to_anchor=(1, 1)``).
    :return: ``matplotlib`` figure, axis.
    """
    # set some default legend kwargs
    legend_kwargs.setdefault("loc", "upper left")
    legend_kwargs.setdefault("bbox_to_anchor", (1, 1))
    legend_kwargs.setdefault("title", title)

    # tags are on every 2 axis pair
    t1, t2 = p2cp.axes_list[:2]

    if line_kwargs is None:
        line_kwargs = {}

    tags = p2cp.tags[:] if tags is None else list(np.array(tags).flatten())

    kwargs = [
        p2cp._hiveplot.hive_plot_edges[t1][t2][key]["edge_kwargs"].copy()
        for key in tags
    ]

    # add / overwrite line kwargs with any additionally supplied kwargs
    for kwarg in kwargs:
        for k in line_kwargs:
            kwarg[k] = line_kwargs[k]

    leg = [Line2D([0, 0], [0, 0], label=key, **kwargs[k]) for k, key in enumerate(tags)]

    ax.legend(handles=leg, **legend_kwargs)

    return fig, ax
