# base.py

"""
Base (viz back-end-agnostic) functionality for visualizations in ``hiveplotlib``.
"""

import re
import warnings
from typing import Hashable, List, Literal, Tuple, Union

import pandas as pd

from hiveplotlib import Axis, BaseHivePlot, HivePlot
from hiveplotlib.exceptions import InvalidHoverVariableError


def get_axis_label_alignment(
    axis: Axis,
    backend: Literal["matplotlib", "bokeh", "holoviews", "plotly"],
    horizontal_angle_span: float = 60,
    vertical_angle_span: float = 60,
) -> Tuple[Literal["bottom", "middle", "top"], Literal["left", "center", "right"]]:
    """
    Generate appropriate horizontal and vertical alignment for text at the radial end point of an ``Axis`` instance.

    ``horizontal_angle_span`` and ``vertical_angle_span`` dictate the text alignment partition, measured in degrees. See
    the below parameter descriptions for how each value is used to partition the angle space.

    :param axis: ``Axis`` for which to generate the appropriate text alignment.
    :param backend: which plotting back end to use. (Different back ends have different string names for their
        alignment options.)
    :param horizontal_angle_span: ``[-horizontal_angle_span, horizontal_angle_span]`` will be ``"left"`` aligned.
        ``[180 - horizontal_angle_span, 180 + horizontal_angle_span]`` will be ``right`` aligned, and all other angles
        will be ``"center"`` aligned.
    :param vertical_angle_span: ``[90 - vertical_angle_span, 90 + vertical_angle_span]`` will be ``"bottom"`` aligned.
        ``[270 - vertical_angle_span, 270 + vertical_angle_span]`` will be ``top`` aligned, and all other angles
        will be ``"middle"`` aligned.
    :return: vertical alignment string and horizontal alignment string appropriate for the edge of the provided
        ``Axis`` instance.
    """
    horizontal_alignment_dict = {"left": "left", "center": "center", "right": "right"}
    vertical_alignment_dict = {"bottom": "bottom", "middle": "middle", "top": "top"}

    # matplotlib and holoviews have different naming convention than default
    if backend in ["matplotlib", "holoviews"]:
        vertical_alignment_dict["middle"] = "center"

    # range in each direction from 0, 180 to specify horizontal alignment
    if (
        axis.angle >= 360 - horizontal_angle_span
        or axis.angle <= 0 + horizontal_angle_span
    ):
        horizontalalignment = horizontal_alignment_dict["left"]
    elif 180 + horizontal_angle_span >= axis.angle >= 180 - horizontal_angle_span:
        horizontalalignment = horizontal_alignment_dict["right"]
    else:
        horizontalalignment = horizontal_alignment_dict["center"]

    # range in each direction from 90, 270 to specify vertical alignment
    if 90 + vertical_angle_span >= axis.angle >= 90 - vertical_angle_span:
        verticalalignment = vertical_alignment_dict["bottom"]
    elif 270 - vertical_angle_span <= axis.angle <= 270 + vertical_angle_span:
        verticalalignment = vertical_alignment_dict["top"]
    else:
        verticalalignment = vertical_alignment_dict["middle"]

    return verticalalignment, horizontalalignment


def edge_viz_preparation(
    hive_plot: Union[BaseHivePlot, HivePlot],
    name: Literal["Hive Plot", "P2CP"],
    from_axis: Hashable,
    to_axis: Hashable,
    tag: Hashable,
    already_warned_p2cp_tags: List[Hashable],
    edge_kwargs: dict,
    line_width_name: str,
    line_alpha_name: str,
    line_color_name: str,
    default_line_width: float = 1.5,
    default_line_alpha: float = 0.5,
    default_line_color: str = "black",
    include_line_color: bool = True,
    include_line_alpha: bool = True,
    include_line_width: bool = True,
) -> Tuple[dict, List[Hashable]]:
    """
    Warning checks and keyword argument tracking specifically for ``edge_viz()`` for a subset of edges to plot.

    This code is abstracted to ``hiveplotlib.viz.base`` to avoid redundancy for the ``edge_viz()`` calls with the
    various back ends, but this function not intended for use outside of within ``edge_viz()``.

    :param hive_plot: underlying hive plot to plot. Should never provide a ``P2CP`` instance here.
    :param name: "Hive Plot" or "P2CP" being plotted (this affects which warning checks to perform).
    :param from_axis: the "from" axis of edges currently being prepared for viz.
    :param to_axis: the "to" axis of edges currently being prepared for viz.
    :param tag: which tag of edges we are plotting.
    :param already_warned_p2cp_tags: which tags we've already warned about (this avoids repeated warnings when plotting
        ill-specified P2CPs).
    :param edge_kwargs: user-provided edge kwargs to an ``edge_viz()`` call.
    :param line_width_name: name of line width for viz back end.
    :param line_alpha_name: name of line alpha for viz back end.
    :param line_color_name: name of line color for viz back end.
    :param default_line_width: default line width value.
    :param default_line_alpha: default line alpha value.
    :param default_line_color: default line color value.
    :param include_line_color: whether to include the line color parameter or not. (We always want line color, but the
        ``matplotlib`` back end requires some case control with ``color`` vs ``array`` as the color input, so we need
        to do some custom handling in the mpl edge viz without filling in any default ``color`` value.
    :param include_line_alpha: whether to include the line alpha parameter or not. (We always want line alpha, but the
        ``plotly`` back end requires including line alpha via the RGBA value, as standalone line alpha is not supported
        for lines in ``plotly``.)
    :param include_line_width: whether to include the line width parameter or not. (All viz back ends have a line width,
        but the historical ``matplotlib`` implementation did not set a default width, which we will preserve going
        forward.)
    :return: dictionary of the resulting kwargs for the given edges being plotted and a list of P2CP tags that have been
        warned about (the provided ``tag`` will be added if the provided P2CP is ill-specified).
    """
    temp_edge_kwargs = edge_kwargs.copy()

    # only run plotting of edges that exist
    if "curves" in hive_plot.hive_plot_edges[from_axis][to_axis][tag]:
        # create edge_kwargs key if needed
        if "edge_kwargs" not in hive_plot.hive_plot_edges[from_axis][to_axis][tag]:
            hive_plot.hive_plot_edges[from_axis][to_axis][tag]["edge_kwargs"] = {}

        # don't use kwargs specified in this function call if already specified
        for k in list(temp_edge_kwargs.keys()):
            if k in hive_plot.hive_plot_edges[from_axis][to_axis][tag]["edge_kwargs"]:
                if name == "Hive Plot":
                    if isinstance(hive_plot, HivePlot):
                        warnings.warn(
                            f"Specified kwarg '{k}' but already set as kwarg for edge tag {tag} "
                            f"going from edges {from_axis} to {to_axis}. Preserving kwargs already set.\n"
                            "(These kwargs can be changed using the `update_edges()` method "
                            "for your `HivePlot` instance)",
                            stacklevel=3,
                        )
                    elif isinstance(hive_plot, BaseHivePlot):
                        warnings.warn(
                            f"Specified kwarg '{k}' but already set as kwarg for edge tag {tag} "
                            f"going from edges {from_axis} to {to_axis}. Preserving kwargs already set.\n"
                            "(These kwargs can be changed using the `add_edge_kwargs()` method "
                            "for your `BaseHivePlot` instance)",
                            stacklevel=3,
                        )
                    else:  # pragma: no cover
                        raise NotImplementedError(
                            "No instances should ever reach this point..."
                        )
                # only warn once per tag over all axes
                elif name == "P2CP" and tag not in already_warned_p2cp_tags:
                    warnings.warn(
                        f"Specified kwarg '{k}' but already set as kwarg for edge tag {tag}. "
                        f"Preserving kwargs already set.\n"
                        "(These kwargs can be changed using the `add_edge_kwargs()` method "
                        "for your `P2CP` instance)",
                        stacklevel=3,
                    )
                    already_warned_p2cp_tags.append(tag)
                del temp_edge_kwargs[k]

        # some default kwargs for the axes if not specified anywhere
        if (
            line_color_name
            not in hive_plot.hive_plot_edges[from_axis][to_axis][tag]["edge_kwargs"]
            and line_color_name not in temp_edge_kwargs
            and include_line_color
            and (
                hive_plot.edges is None
                or line_color_name not in hive_plot.edges.edge_viz_kwargs[tag]
            )
        ):
            temp_edge_kwargs[line_color_name] = default_line_color
        if (
            line_alpha_name
            not in hive_plot.hive_plot_edges[from_axis][to_axis][tag]["edge_kwargs"]
            and line_alpha_name not in temp_edge_kwargs
            and include_line_alpha
            and (
                hive_plot.edges is None
                or line_alpha_name not in hive_plot.edges.edge_viz_kwargs[tag]
            )
        ):
            temp_edge_kwargs[line_alpha_name] = default_line_alpha
        if (
            line_width_name
            not in hive_plot.hive_plot_edges[from_axis][to_axis][tag]["edge_kwargs"]
            and line_width_name not in temp_edge_kwargs
            and include_line_width
            and (
                hive_plot.edges is None
                or line_width_name not in hive_plot.edges.edge_viz_kwargs[tag]
            )
        ):
            temp_edge_kwargs[line_width_name] = default_line_width

    return temp_edge_kwargs, already_warned_p2cp_tags


def hover_input_check(
    hover: Union[
        bool,
        Literal["nodes", "edges", "axes"],
        list[Literal["nodes", "edges", "axes"],],
    ],
) -> None:
    """
    Raise ``InvalidHoverVariableError`` if invalid ``hover`` value provided.

    :param hover: value for ``hover`` parameter to check.
    :raises InvalidHoverVariableError: if invalid input provided to ``hover`` parameter.
    """
    if not isinstance(hover, bool):
        if isinstance(hover, str):
            hover = [hover]
        if pd.api.types.is_list_like(hover):
            for h in hover:
                if h not in ["nodes", "edges", "axes"]:
                    raise InvalidHoverVariableError(
                        "Hover information is only supported for `'nodes'`, `'axes'`, and / or `'edges'` "
                        f"(provided values: {hover})"
                    )
    return


def get_hover_axis_metadata(axis: Axis) -> pd.DataFrame:
    """
    Return ``pandas.DataFrame`` of ``axis`` metadata for axis hover information.

    Used for axis hover info for interactive back ends.

    .. note::
        This function returns 2 rows of redundant data (this works better for some of the backends since an axis is
        composed of two data points, start and end).

    :param axis: axis from which to grab metadata.
    :return: dataframe of axis metadata.
    """
    # start with axis metadata + specific params, prioritizing axis metadata over params
    metadata = axis.__dict__.copy()
    metadata.update(axis.metadata.copy())

    del metadata["node_placements"]
    del metadata["start"]
    del metadata["end"]
    del metadata["inferred_vmin"]
    del metadata["inferred_vmax"]
    del metadata["polar_start"]
    del metadata["polar_end"]
    del metadata["metadata"]
    return pd.DataFrame(metadata, index=[0, 1])


def __sanitize_dataframe_columns(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:  # pragma: no cover
    """
    Sanitize column names in a DataFrame, replacing spaces / special characters with underscores.

    .. note::
        This function is useful for ensuring that column names are valid for plotting with ``holoviews-bokeh`` or
        ``bokeh`` hover tools.

        These special characters would otherwise cause issues with those hover tooltips.

    param df: the input DataFrame.

    :return: tuple containing a new DataFrame with sanitized column names and a dictionary mapping original column
        names to sanitized names.
    """
    sanitized_df = df.copy()
    original_to_sanitized_map = {}

    for original_col_name in df.columns:
        # strip leading/trailing whitespace first
        stripped_name = original_col_name.strip()
        # replace non-word characters (except underscore) and spaces with underscores
        sanitized_name = re.sub(r"[^\w]+", "_", stripped_name)
        # handle cases where the original name started with a non-word character
        sanitized_name = sanitized_name.strip("_")
        # ensure it's not an empty string if original was just special chars
        if not sanitized_name:
            sanitized_name = "sanitized_column"
        # make sure the sanitized name is unique, if necessary
        while (
            sanitized_name in sanitized_df.columns
            and original_to_sanitized_map.get(original_col_name) != sanitized_name
        ):
            sanitized_name += "_sanitized"

        sanitized_df = sanitized_df.rename(columns={original_col_name: sanitized_name})
        original_to_sanitized_map[original_col_name] = sanitized_name

    return sanitized_df, original_to_sanitized_map
