# input_checks.py

"""
Functions to check inputs for input-agnostic viz functions in the ``hiveplotlib.viz`` module.
"""

import warnings
from typing import Literal, Tuple, Union

from hiveplotlib import P2CP, BaseHivePlot, HivePlot


def input_check(
    instance: Union[HivePlot, BaseHivePlot, P2CP],
    objects_to_plot: Literal["nodes", "axes", "edges"],
) -> Tuple[Union[BaseHivePlot, HivePlot], Literal["Hive Plot", "P2CP"], bool]:
    """
    Check whether a provided instance is supported by the instance-agnostic plotting tools.

    Also raise a warning if the user is trying to plot an aspect of a hive plot / P2CP that hasn't yet been created.

    Current supported data structures are :py:class:`~hiveplotlib.HivePlot()`,
    :py:class:`~hiveplotlib.BaseHivePlot()`, and :py:class:`~hiveplotlib.P2CP()` instances.

    :param instance: instance to plot.
    :param objects_to_plot: which type of objects being plotted. This will be used to raise more informative warnings to
        the user.
    :return: the underlying ``HivePlot`` or ``BaseHivePlot`` instance (all the plotting is based on a ``HivePlot`` /
        ``BaseHivePlot`` object, even the ``P2CP`` instance), plus a string of the name of the instance (for more clear
        warning for downstream viz calls), and a ``bool`` of whether a warning was raised.
    :raises NotImplementedError: if anything other than a ``HivePlot``, ``BaseHivePlot``, or ``P2CP`` instance
        provided.
    """
    if isinstance(instance, HivePlot):
        hive_plot = instance
        name = "Hive Plot"
    if isinstance(instance, BaseHivePlot):
        hive_plot = instance
        name = "Hive Plot"
    elif isinstance(instance, P2CP):
        hive_plot = instance._hiveplot
        name = "P2CP"
    else:
        raise NotImplementedError(
            "Can only handle `HivePlot`, `BaseHivePlot`, and `P2CP` instances"
        )

    warning_raised = False

    if objects_to_plot == "axes":
        if len(hive_plot.axes) == 0:
            if isinstance(instance, HivePlot):
                warnings.warn(
                    "No axes have been set up yet. "
                    "Axes can be set up by running `HivePlot.build_hive_plot()`",
                    stacklevel=3,
                )
            elif isinstance(instance, BaseHivePlot):
                warnings.warn(
                    "No axes have been added yet. "
                    "Axes can be added by running `BaseHivePlot.add_axes()`",
                    stacklevel=3,
                )
            elif isinstance(instance, P2CP):
                warnings.warn(
                    "No axes have been set yet. "
                    "Nodes can be placed on axes by running `P2CP.set_axes()`",
                    stacklevel=3,
                )
            warning_raised = True
    elif objects_to_plot == "edges":
        if len(list(hive_plot.hive_plot_edges.keys())) == 0:
            if isinstance(instance, HivePlot):
                warnings.warn(
                    "Your `HivePlot` instance does not have any specified edges yet. "
                    "Edges can be created for plotting by running `HivePlot.build_hive_plot()`",
                    stacklevel=3,
                )
            elif isinstance(instance, BaseHivePlot):
                warnings.warn(
                    "Your `BaseHivePlot` instance does not have any specified edges yet. "
                    "Edges can be created for plotting by running `BaseHivePlot.connect_axes()`",
                    stacklevel=3,
                )
            elif isinstance(instance, P2CP):
                warnings.warn(
                    "Your `P2CP` instance does not have any specified edges yet. "
                    "Edges can be created for plotting by running `P2CP.build_edges()`",
                    stacklevel=3,
                )
            warning_raised = True
    elif objects_to_plot == "nodes":
        # p2cp warning only happens when axes don't exist
        if len(hive_plot.axes) == 0:
            if isinstance(instance, P2CP):
                warnings.warn(
                    "No axes have been set yet, thus no nodes have been placed on axes. "
                    "Nodes can be placed on axes by running `P2CP.set_axes()`",
                    stacklevel=3,
                )
                warning_raised = True
            elif isinstance(instance, HivePlot):
                warnings.warn(
                    "No axes have been set up yet, thus no nodes have been placed on axes. "
                    "Nodes can be placed on axes by running `HivePlot.build_hive_plot()`",
                    stacklevel=3,
                )
                warning_raised = True
        else:
            for axis in hive_plot.axes.values():
                num_to_plot = axis.node_placements.shape[0]
                if num_to_plot == 0:
                    if isinstance(instance, HivePlot):
                        warnings.warn(
                            "At least one of your axes has no nodes placed on it yet. "
                            "Nodes can be placed on axes by running `HivePlot.build_hive_plot()`",
                            stacklevel=3,
                        )
                    elif isinstance(instance, BaseHivePlot):
                        warnings.warn(
                            "At least one of your axes has no nodes placed on it yet. "
                            "Nodes can be placed on axes by running `BaseHivePlot.place_nodes_on_axis()`",
                            stacklevel=3,
                        )
                    warning_raised = True
    else:  # pragma: no cover
        raise NotImplementedError(
            f"`objects_to plot` must be one of 'axes', 'edges', or 'nodes', but user provided '{objects_to_plot}'."
        )

    return hive_plot, name, warning_raised
