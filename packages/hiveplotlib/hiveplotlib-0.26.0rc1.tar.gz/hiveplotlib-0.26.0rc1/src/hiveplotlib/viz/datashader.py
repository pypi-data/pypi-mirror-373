# datashader.py

"""
Datashading capabilities for ``hiveplotlib``.
"""

import warnings
from typing import Hashable, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors
from matplotlib.image import AxesImage

from hiveplotlib import P2CP, BaseHivePlot, HivePlot
from hiveplotlib.viz.input_checks import input_check
from hiveplotlib.viz.matplotlib import axes_viz

try:
    import datashader as ds
    import seaborn as sns
except ImportError as ie:  # pragma: no cover
    raise ImportError(
        "Datashader or seaborn not installed, but can be installed by running "
        "`pip install hiveplotlib[datashader]`"
    ) from ie


def datashade_edges_mpl(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    tag: Optional[Hashable] = None,
    cmap: Optional[Union[str, colors.ListedColormap]] = None,
    vmin: float = 1,
    vmax: Optional[float] = None,
    log_cmap: bool = True,
    pixel_spread: int = 2,
    reduction: Optional[ds.reductions.Reduction] = None,
    buffer: float = 0.1,
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[float, float] = (10, 10),
    dpi: int = 300,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    **im_kwargs,
) -> Tuple[plt.Figure, plt.Axes, AxesImage]:
    """
    ``matplotlib`` visualization of constructed edges in a ``HivePlot`` or ``P2CP`` instance using ``datashader``.

    The main idea of ``datashader`` is rather than plot all the lines on top of each other in a figure, one can instead
    essentially build up a single 2d image of the lines in 2-space. We can then plot just this rasterization, which is
    much smaller. By using the default reduction function ``reduction=ds.count`` (counting values in bins),
    we are essentially building a 2d histogram. For more on reductions in ``datashader``, see the
    `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a complete
    list of reduction functions available, see the
    `datashader API docs <https://datashader.org/api.html#reductions>`__.

    .. note::
        A high ``dpi`` value is recommended when datashading to allow for more nuance in the rasterization. This is why
        this visualization function defaults to a ``dpi`` value of 300 when ``fig=None`` and ``ax=None``.

        Experimentation with different (low) values for ``pixel_spread`` is encouraged. As the name suggests, this
        parameter spreads out calculated pixel values in the rasterization radially. Values that are too low tends to
        result in the thinner, more isolated curves "breaking apart" in the final visualization. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.

        Any provided edge plotting keyword arguments in ``HivePlot.edges.edge_viz_kwargs`` will be disregarded in this
        visualization, as this flexibility is reserved for datashading the edges. Inclusion of any edge kwargs here
        as part of the ``im_kwargs`` will likely trigger an error.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param tag: which tag of data to plot. If ``None`` is provided, then plotting will occur if there is only one tag
        in the instance. For more on data tags, see further discussion in the Comparing Network Subgroups
        `Notebook <../../notebooks/comparing_network_subgroups.ipynb>`__.
    :param cmap: which colormap to use for the datashaded edges. Default uses a ``seaborn`` colormap similar to the
        ``matplotlib`` ``"Blues"`` colormap.
    :param vmin: minimum value used in the colormap for plotting the rasterization of curves. Default 1.
    :param vmax: maximum value used in the colormap for plotting the rasterization of curves. Default ``None`` finds and
        uses the maximum bin value of the calculated rasterization.
    :param log_cmap: whether to use a logarithmic (base 10) scale for the colormap. Default ``True``.
    :param reduction: the means of projecting from data space to pixel space for the rasterization. Default ``None``
        uses ``ds.count()``, essentially building a 2d histogram. For more on reductions in ``datashader``, see the
        `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a
        complete list of reduction functions available, see the
        `datashader API docs <https://datashader.org/api.html#reductions>`__.
    :param pixel_spread: amount of pixel units in which to "spread" pixel values in the resulting rasterization before
        plotting. Default amount of spreading is 2 pixels. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param fig: default ``None`` builds new figure. If a figure is specified, ``Axis`` instances will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, ``Axis`` instances will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param dpi: resolution (Dots Per Inch) of resulting figure. A higher-than-usual DPI is recommended to show more
        pixels in the final rasterization, which will show more nuance.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param im_kwargs: additional params that will be applied to the final ``plt.imshow()`` call on the rasterization.
        Must not clash with the `cmap`, `vmin`, or `vmax` parameters.
    :return: ``matplotlib`` figure, axis, image. If there are no edges to plot, the returned image will be ``None``.
    """
    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="edges")

    if cmap is None:
        cmap = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)
    if reduction is None:
        reduction = ds.count()
    if fig_kwargs is None:
        fig_kwargs = {}

    # allow for plotting onto specified figure, axis
    if fig is None and ax is None:
        if "figsize" not in fig_kwargs:
            fig_kwargs["figsize"] = figsize
        if dpi not in fig_kwargs:
            fig_kwargs["dpi"] = dpi
        fig, ax = plt.subplots(**fig_kwargs)

    # stop plotting if there are no edges to plot
    if warning_raised:
        return fig, ax, None

    # check for all tags in instance if no tag specified
    #  warn that we are only plotting one tag if multiple tags found
    if tag is None:
        tags = set()
        for g1 in hive_plot.hive_plot_edges:
            for g2 in hive_plot.hive_plot_edges[g1]:
                tags |= set(hive_plot.hive_plot_edges[g1][g2].keys())
        tag = sorted(tags)[0]
        if len(tags) > 1:
            warnings.warn(
                f"Multiple tags detected between edges. Only plotting tag {tag}",
                stacklevel=2,
            )

    # always base the extent of the rasterization on the extent of the underlying hive plot / P2CP
    max_radius = max([axis.polar_end for axis in hive_plot.axes.values()])
    # throw in a minor buffer
    buffer_radius = buffer * max_radius
    max_radius += buffer_radius
    xlim = (-max_radius, max_radius)
    ylim = (-max_radius, max_radius)

    # base pixel density of rasterization on DPI of image
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi

    cvs = ds.Canvas(
        x_range=xlim, y_range=ylim, plot_height=int(height), plot_width=int(width)
    )

    # aggregate the edges into a single dataframe before datashading
    all_edges = [
        pd.DataFrame(np.empty(shape=(0, 2)), columns=["x", "y"])
    ]  # lets us plot without error if empty
    for g1 in hive_plot.hive_plot_edges:
        for g2 in hive_plot.hive_plot_edges[g1]:
            curves_shape = hive_plot.hive_plot_edges[g1][g2][tag]["curves"].shape[0]

            ids_shape = hive_plot.hive_plot_edges[g1][g2][tag]["ids"].shape[0]

            # only aggregate if there are edges to plot
            if curves_shape > 0:
                repeat_num = curves_shape / ids_shape
                edge_curves = hive_plot.hive_plot_edges[g1][g2][tag]["curves"]
                if hive_plot.edges is not None:
                    edge_metadata = hive_plot.edges._data[tag][
                        hive_plot.edges.relevant_edges[g1][g2][tag]
                    ].drop(
                        columns=[
                            hive_plot.edges.from_column_name,
                            hive_plot.edges.to_column_name,
                        ]
                    )
                    edge_metadata_columns = edge_metadata.columns
                    edge_info = {
                        col: np.repeat(edge_metadata[col].to_numpy(), repeat_num)
                        for col in edge_metadata_columns
                    }
                else:
                    edge_info = {}

                edge_info["x"] = edge_curves[:, 0]
                edge_info["y"] = edge_curves[:, 1]

                all_edges.append(pd.DataFrame(edge_info))

    all_edges = pd.concat(all_edges, ignore_index=True)

    lines = ds.transfer_functions.spread(
        cvs.line(all_edges, "x", "y", agg=reduction), px=pixel_spread
    )

    lines_np = lines.to_numpy()

    # if reduction is column based, not count based, we need to correct based on density
    if reduction not in [ds.count(), ds.any()]:
        lines_density = ds.transfer_functions.spread(
            cvs.line(all_edges, "x", "y", agg=ds.count()), px=pixel_spread
        )
        lines_np = lines_np / lines_density.to_numpy()

    if vmax is None:
        vmax = np.nanmax(lines_np)

    if log_cmap:
        im_kwargs["norm"] = colors.LogNorm(vmin=vmin, vmax=vmax)
    else:
        im_kwargs["vmin"] = vmin
        im_kwargs["vmax"] = vmax

    if axes_off:
        ax.axis("off")

    im = ax.imshow(
        np.ma.masked_where(lines_np == 0, lines_np),
        extent=[*xlim, *ylim],
        origin="lower",
        cmap=cmap,
        **im_kwargs,
    )

    return fig, ax, im


def datashade_nodes_mpl(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    cmap: Union[str, colors.ListedColormap] = "copper",
    vmin: float = 1,
    vmax: Optional[float] = None,
    log_cmap: bool = True,
    pixel_spread: int = 15,
    reduction: Optional[ds.reductions.Reduction] = None,
    buffer: float = 0.1,
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[float, float] = (10, 10),
    dpi: int = 300,
    axes_off: bool = True,
    fig_kwargs: Optional[dict] = None,
    **im_kwargs,
) -> Tuple[plt.Figure, plt.Axes, AxesImage]:
    """
    ``matplotlib`` visualization of nodes / points in a ``HivePlot`` / ``P2CP`` instance using ``datashader``.

    The main idea of ``datashader`` is rather than plot all the points on top of each other in a figure, one can instead
    essentially build up a single 2d image of the points in 2-space. We can then plot just this rasterization, which is
    much smaller. By using the default reduction function ``reduction=ds.count()`` (counting values in bins),
    we are essentially building a 2d histogram. For more on reductions in ``datashader``, see the
    `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a complete
    list of reduction functions available, see the
    `datashader API docs <https://datashader.org/api.html#reductions>`__.

    .. note::
        A high ``dpi`` value is recommended when datashading to allow for more nuance in the rasterization. This is why
        this visualization function defaults to a ``dpi`` value of 300 when ``fig=None`` and ``ax=None``. Since we are
        interested in *positions* rather than the *lines* from ``hiveplotlib.viz.datashader.datashade_edges_mpl()``,
        though, one will likely need a much larger ``pixel_spread`` value here, on the order of 10 times larger, to see
        the node density well in the final visualization.

        Experimentation with different values for ``pixel_spread`` is encouraged. As the name suggests, this
        parameter spreads out calculated pixel values in the rasterization radially. Values that are too low tends to
        result in smaller, harder to see points in the final visualization. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.

        Any provided node plotting keyword arguments in ``HivePlot.nodes.node_viz_kwargs`` will be disregarded in this
        visualization, as this flexibility is reserved for datashading the nodes. Inclusion of any ``node_kwargs`` here
        will also raise a warning.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to draw edges.
    :param cmap: which colormap to use for the datashaded nodes. Default "copper".
    :param vmin: minimum value used in the colormap for plotting the rasterization of curves. Default 1.
    :param vmax: maximum value used in the colormap for plotting the rasterization of curves. Default ``None`` finds and
        uses the maximum bin value of the calculated rasterization.
    :param log_cmap: whether to use a logarithmic (base 10) scale for the colormap. Default ``True``.
    :param reduction: the means of projecting from data space to pixel space for the rasterization. Default ``None``
        uses ``ds.count()``, essentially building a 2d histogram. For more on reductions in ``datashader``, see the
        `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a
        complete list of reduction functions available, see the
        `datashader API docs <https://datashader.org/api.html#reductions>`__.
    :param pixel_spread: amount of pixel units in which to "spread" pixel values in the resulting rasterization before
        plotting. Default amount of spreading is 15 pixels. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`_.
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param fig: default ``None`` builds new figure. If a figure is specified, ``Axis`` instances will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, ``Axis`` instances will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param dpi: resolution (Dots Per Inch) of resulting figure. A higher-than-usual DPI is recommended to show more
        pixels in the final rasterization, which will show more nuance.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param im_kwargs: additional params that will be applied to the final ``plt.imshow()`` call on the rasterization.
        Must not clash with the `cmap`, `vmin`, or `vmax` parameters.
    :return: ``matplotlib`` figure, axis, image. If there are no nodes to plot, the returned image will be ``None``.
    """
    hive_plot, _, warning_raised = input_check(instance, objects_to_plot="nodes")

    if reduction is None:
        reduction = ds.count()
    if fig_kwargs is None:
        fig_kwargs = {}

    # allow for plotting onto specified figure, axis
    if fig is None and ax is None:
        if "figsize" not in fig_kwargs:
            fig_kwargs["figsize"] = figsize
        if dpi not in fig_kwargs:
            fig_kwargs["dpi"] = dpi
        fig, ax = plt.subplots(**fig_kwargs)

    if warning_raised:
        return fig, ax, None

    # always base the extent of the rasterization on the extent of the underlying hive plot / P2CP
    max_radius = max([axis.polar_end for axis in hive_plot.axes.values()])
    # throw in a minor buffer
    buffer_radius = buffer * max_radius
    max_radius += buffer_radius
    xlim = (-max_radius, max_radius)
    ylim = (-max_radius, max_radius)

    # base pixel density of rasterization on DPI of image
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi

    cvs = ds.Canvas(
        x_range=xlim, y_range=ylim, plot_height=int(height), plot_width=int(width)
    )

    # aggregate the nodes into a single dataframe before datashading
    node_placements = pd.concat(
        [hive_plot.axes[axis_id].node_placements for axis_id in hive_plot.axes]
    )

    points = ds.transfer_functions.spread(
        cvs.points(node_placements, "x", "y", agg=reduction), px=pixel_spread
    )

    points_np = points.to_numpy()

    # if reduction is column based, not count based, we need to correct based on density
    if reduction not in [ds.count(), ds.any()]:
        points_density = ds.transfer_functions.spread(
            cvs.points(node_placements, "x", "y", agg=ds.count()), px=pixel_spread
        )
        points_np = points_np / points_density.to_numpy()

    if vmax is None:
        vmax = np.nanmax(points_np)

    if log_cmap:
        im_kwargs["norm"] = colors.LogNorm(vmin=vmin, vmax=vmax)
    else:
        im_kwargs["vmin"] = vmin
        im_kwargs["vmax"] = vmax

    if axes_off:
        ax.axis("off")

    im = ax.imshow(
        np.ma.masked_where(points_np == 0, points_np),
        extent=[*xlim, *ylim],
        origin="lower",
        cmap=cmap,
        **im_kwargs,
    )

    return fig, ax, im


def datashade_hive_plot_mpl(
    instance: Union[BaseHivePlot, HivePlot, P2CP],
    tag: Optional[Hashable] = None,
    cmap_edges: Optional[Union[str, colors.ListedColormap]] = None,
    cmap_nodes: Union[str, colors.ListedColormap] = "copper",
    vmin_nodes: float = 1,
    vmax_nodes: Optional[float] = None,
    vmin_edges: float = 1,
    vmax_edges: Optional[float] = None,
    node_kwargs: Optional[dict] = None,
    log_cmap_nodes: bool = True,
    pixel_spread_nodes: int = 15,
    reduction_nodes: Optional[ds.reductions.Reduction] = None,
    log_cmap_edges: bool = True,
    pixel_spread_edges: int = 2,
    reduction_edges: Optional[ds.reductions.Reduction] = None,
    fig: Optional[plt.Figure] = None,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[float, float] = (10, 10),
    dpi: int = 300,
    axes_off: bool = True,
    buffer: float = 0.1,
    show_axes_labels: bool = True,
    axes_labels_buffer: float = 1.1,
    axes_labels_fontsize: int = 16,
    axes_kwargs: Optional[dict] = None,
    text_kwargs: Optional[dict] = None,
    fig_kwargs: Optional[dict] = None,
    **edge_kwargs,
) -> Tuple[plt.Figure, plt.Axes, AxesImage, AxesImage]:
    """
    ``matplotlib`` visualization of a ``HivePlot`` or ``P2CP`` instance using ``datashader``.

    Plots both nodes and edges with datashader along with standard hive plot / P2CP axes.

    The main idea of ``datashader`` is rather than plot all the lines on top of each other in a figure, one can instead
    essentially build up a single 2d image of the lines in 2-space. We can then plot just this rasterization, which is
    much smaller. By using the default reduction function ``ds.count()`` (counting values in bins),
    we are essentially building a 2d histogram. For more on reductions in ``datashader``, see the
    `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a complete
    list of reduction functions available, see the
    `datashader API docs <https://datashader.org/api.html#reductions>`__.

    .. note::
        A high ``dpi`` value is recommended when datashading to allow for more nuance in the rasterization. This is why
        this visualization function defaults to a ``dpi`` value of 300 when ``fig=None`` and ``ax=None``.

        Experimentation with different (low) values for ``pixel_spread_nodes`` and ``pixel_spread_edges`` is encouraged.
        As the name suggests, this parameter spreads out calculated pixel values in the rasterization radially. Values
        that are too low tends to result in the thinner, more isolated curves "breaking apart" in the final
        visualization. For more on spreading, see the
        `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.

        Any provided node plotting keyword arguments in ``HivePlot.nodes.node_viz_kwargs`` will be disregarded in this
        visualization, as this flexibility is reserved for datashading the nodes. Inclusion of any ``node_kwargs`` here
        will also raise a warning.

        Any provided edge plotting keyword arguments in ``HivePlot.edges.edge_viz_kwargs`` will be disregarded in this
        visualization, as this flexibility is reserved for datashading the edges. Inclusion of any edge kwargs here
        as part of the ``im_kwargs`` will likely trigger an error.

    :param instance: ``HivePlot`` or ``P2CP`` instance for which we want to visualize.
    :param tag: which tag of data to plot. If ``None`` is provided, then plotting will occur if there is only one tag
        in the instance. For more on data tags, see further discussion in the Comparing Network Subgroups
        `Notebook <../../notebooks/comparing_network_subgroups.ipynb>`__.
    :param cmap_edges: which colormap to use for the datashaded edges. Default uses a ``seaborn`` colormap similar to
        the ``matplotlib`` ``"Blues"`` colormap.
    :param cmap_nodes: which colormap to use for the datashaded nodes. Default "copper".
    :param vmin_nodes: minimum value used in the colormap for plotting the rasterization of nodes. Default 1.
    :param vmax_nodes: maximum value used in the colormap for plotting the rasterization of nodes. Default ``None``
        finds and uses the maximum bin value of the calculated rasterization.
    :param vmin_edges: minimum value used in the colormap for plotting the rasterization of edges. Default 1.
    :param vmax_edges: maximum value used in the colormap for plotting the rasterization of edges. Default ``None``
        finds and uses the maximum bin value of the calculated rasterization.
    :param node_kwargs: additional params that will be applied to the final ``plt.imshow()`` call on the edge
        rasterization. Must not clash with the `cmap_nodes`, `vmin_nodes`, or `vmax_nodes` parameters.
    :param log_cmap_nodes: whether to use a logarithmic (base 10) scale for the colormap. Default ``True``.
    :param pixel_spread_nodes: amount of pixel units in which to "spread" pixel values in the resulting rasterization
        before plotting. Default amount of spreading is 15 pixels. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.
    :param reduction_nodes: the means of projecting from data space to pixel space for the rasterization of nodes.
        Default ``None`` uses ``ds.count()``, essentially building a 2d histogram. For more on reductions in
        ``datashader``, see the
        `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a
        complete list of reduction functions available, see the
        `datashader API docs <https://datashader.org/api.html#reductions>`__.
    :param log_cmap_edges: whether to use a logarithmic (base 10) scale for the colormap. Default ``True``.
    :param pixel_spread_edges: amount of pixel units in which to "spread" pixel values in the resulting rasterization
        before plotting. Default amount of spreading is 2 pixels. For more on spreading,
        see the `datashader documentation <https://datashader.org/getting_started/Pipeline.html#spreading>`__.
    :param reduction_edges: the means of projecting from data space to pixel space for the rasterization of edges.
        Default ``None`` uses ``ds.count()``, essentially building a 2d histogram. For more on reductions in
        ``datashader``, see the
        `datashader documentation <https://datashader.org/getting_started/Pipeline.html#d-reductions>`__, and for a
        complete list of reduction functions available, see the
        `datashader API docs <https://datashader.org/api.html#reductions>`__.
    :param fig: default ``None`` builds new figure. If a figure is specified, ``Axis`` instances will be
        drawn on that figure. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param ax: default ``None`` builds new axis. If an axis is specified, ``Axis`` instances will be drawn on that
        axis. Note: ``fig`` and ``ax`` must BOTH be ``None`` to instantiate new figure and axes.
    :param figsize: size of figure. Note: only works if instantiating new figure and axes (e.g. ``fig`` and ``ax`` are
        ``None``).
    :param dpi: resolution (Dots Per Inch) of resulting figure. A higher-than-usual DPI is recommended to show more
        pixels in the final rasterization, which will show more nuance.
    :param axes_off: whether to turn off Cartesian x, y axes in resulting ``matplotlib`` figure (default ``True``
        hides the x and y axes).
    :param buffer: fraction of the axes past which to buffer x and y dimensions (e.g. setting ``buffer`` to 0.1 will
        find the maximum radius spanned by any ``Axis`` instance and set the x and y bounds as
        ``(-max_radius - buffer * max_radius, max_radius + buffer * max_radius)``).
    :param show_axes_labels: whether to label the hive plot axes in the figure (uses ``Axis.long_name`` for each
        ``Axis``.)
    :param axes_labels_buffer: fraction which to radially buffer axes labels (e.g. setting ``axes_label_buffer`` to 1.1
        will be 10% further past the end of the axis moving from the origin of the plot).
    :param axes_labels_fontsize: font size for hive plot axes labels.
    :param axes_kwargs: additional params that will be applied to all axes. Note, these are kwargs that affect
        a ``plt.plot()`` call.
    :param text_kwargs: additional kwargs passed to ``plt.text()`` call.
    :param fig_kwargs: additional values to be called in ``plt.subplots()`` call. Note if ``figsize`` is added here,
        then it will be prioritized over the ``figsize`` parameter.
    :param edge_kwargs: additional params that will be applied to the final ``plt.imshow()`` call on the edge
        rasterization. Must not clash with the `cmap_edges`, `vmin_edges`, or `vmax_edges` parameters.
    :return: ``matplotlib`` figure, axis, the image corresponding to node data, and the image corresponding to edge
        data. If there are no edges / nodes to plot, the returned edges image / nodes image will be ``None``.
    """
    if cmap_edges is None:
        cmap_edges = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)
    if reduction_nodes is None:
        reduction_nodes = ds.count()
    if reduction_edges is None:
        reduction_edges = ds.count()
    if axes_kwargs is None:
        axes_kwargs = {}
    if node_kwargs is None:
        node_kwargs = {}

    fig, ax, im_edges = datashade_edges_mpl(
        instance=instance,
        tag=tag,
        fig=fig,
        ax=ax,
        buffer=buffer,
        cmap=cmap_edges,
        vmin=vmin_edges,
        vmax=vmax_edges,
        log_cmap=log_cmap_edges,
        reduction=reduction_edges,
        pixel_spread=pixel_spread_edges,
        figsize=figsize,
        dpi=dpi,
        axes_off=axes_off,
        fig_kwargs=fig_kwargs,
        **edge_kwargs,
    )

    axes_viz(
        instance=instance,
        fig=fig,
        ax=ax,
        buffer=buffer,
        show_axes_labels=show_axes_labels,
        axes_labels_buffer=axes_labels_buffer,
        axes_labels_fontsize=axes_labels_fontsize,
        axes_off=axes_off,
        text_kwargs=text_kwargs,
        **axes_kwargs,
    )

    fig, ax, im_nodes = datashade_nodes_mpl(
        instance=instance,
        fig=fig,
        ax=ax,
        buffer=buffer,
        cmap=cmap_nodes,
        vmin=vmin_nodes,
        vmax=vmax_nodes,
        log_cmap=log_cmap_nodes,
        reduction=reduction_nodes,
        pixel_spread=pixel_spread_nodes,
        axes_off=axes_off,
        **node_kwargs,
        zorder=2,
    )

    return fig, ax, im_nodes, im_edges


# alias consistent naming options with other APIs
hive_plot_viz = datashade_hive_plot_mpl
node_viz = datashade_nodes_mpl
edge_viz = datashade_edges_mpl
