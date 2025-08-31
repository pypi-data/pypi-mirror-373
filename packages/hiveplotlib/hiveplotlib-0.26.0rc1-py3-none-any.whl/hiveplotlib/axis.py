# axis.py

"""
Definition of ``Axis`` instance and helper static methods for generating and working with ``Axis`` instances.
"""

from typing import Hashable, Optional

import pandas as pd

from hiveplotlib.utils import polar2cartesian


class Axis:
    """
    ``Axis`` instance.

    ``Axis`` instances are initialized based on their intended final position when plotted. Each ``Axis`` is also
    initialized with a unique, hashable ``axis_id`` for clarity when building hive plots with multiple axes.

    The eventual size and positioning of the ``Axis`` instance is dictated in the context of polar coordinates by three
    parameters:

    ``start`` dictates the distance from the origin to the *beginning* of the axis when eventually plotted.

    ``stop`` dictates the distance from the origin to the *end* of the axis when eventually plotted.

    ``angle`` sets the angle the ``Axis`` is rotated counterclockwise. For example, ``angle=0`` points East,
    ``angle=90`` points North, and ``angle=180`` points West.

    ``Node`` instances placed on each ``Axis`` instance will be scaled to fit onto the span of the ``Axis``, but this is
    discussed further in the ``HivePlot`` class, which handles this placement.

    Since ``axis_id`` values may be shorthand for easy referencing when typing code, if one desires a formal name to
    plot against each axis when visualizing, one can provide a separate ``long_name`` that will show up as the axis
    label when running ``hiveplotlib.viz`` code. (For example, one may choose ``axis_id="a1"`` and
    ``long_name="Axis 1"``.

    .. note::
        ``long_name`` defaults to ``axis_id`` if not specified.

    :example:

        .. highlight:: python
        .. code-block:: python

            # 3 axes, spaced out 120 degrees apart, all size 4, starting 1 unit off of origin
            axis0 = Axis(axis_id="a0", start=1, end=5, angle=0, long_name="Axis 0")
            axis1 = Axis(axis_id="a1", start=1, end=5, angle=120, long_name="Axis 1")
            axis2 = Axis(axis_id="a2", start=1, end=5, angle=240, long_name="Axis 2")
    """

    def __init__(
        self,
        axis_id: Hashable,
        start: float = 1,
        end: float = 5,
        angle: float = 0,
        long_name: Optional[Hashable] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Initialize ``Axis`` object with start and end positions and angle. Default to axis normalized on [0, 1].

        :param axis_id: unique name for ``Axis`` instance.
        :param start: point closest to the center of the plot (using the same positive number for multiple axes in a
            hive plot is a nice way to space out the figure).
        :param end: point farthest from the center of the plot.
        :param angle: angle to set the axis, in degrees (moving counterclockwise, e.g.
            0 degrees points East, 90 degrees points North).
        :param long_name: longer name for use when labeling on graph (but not for referencing the axis).
            Default ``None`` sets it to ``axis_id``.
        :param metadata: optional dictionary of metadata to attach to the axis.
            Default ``None`` means no metadata is attached.
        """
        self.axis_id = axis_id

        if long_name is None:
            self.long_name = str(axis_id)
        else:
            self.long_name = str(long_name)

        # keep internal angle in [0, 360)
        self.angle = angle % 360

        self.polar_start = start
        self.start = polar2cartesian(self.polar_start, self.angle)

        self.polar_end = end
        self.end = polar2cartesian(self.polar_end, self.angle)

        # hold the current sorting variable used to place nodes on an axis in a ``HivePlot`` instance.
        self.sorting_variable = None

        # hold all the cartesian coordinates, polar rho, corresponding labels, and node metadata in a pandas dataframe
        self.node_placements = pd.DataFrame(columns=["x", "y", "unique_id", "rho"])

        # hold the current vmin and vmax used to place nodes on an axis in a ``HivePlot`` instance.
        self.vmin = None
        self.vmax = None

        # hold whether current vmin and vmax used to place nodes on an axis in a ``HivePlot`` instance were inferred.
        self.inferred_vmin = None
        self.inferred_vmax = None

        self.metadata = metadata if metadata is not None else {}

    def __str__(self) -> str:
        """
        Make more human-readable, multiline representation for ``Axis`` instance.
        """
        return (
            f"hiveplotlib.Axis '{self.axis_id}'\n"
            f"Current data vmin: {self.vmin}\n"
            f"Current data vmax: {self.vmax}\n"
            f"Current sorting variable used to place nodes on this axis: '{self.sorting_variable}'\n"
            f"Current polar start: {self.polar_start}\n"
            f"Current polar end: {self.polar_end}\n"
            f"Current angle: {self.angle}\n"
            f"Inferred vmin: {self.inferred_vmin}\n"
            f"Inferred vmax: {self.inferred_vmax}\n"
            f"Long name: '{self.long_name}'"
        )

    def __repr__(self) -> str:
        """
        Make custom repr for ``Axis`` instance.
        """
        return (
            f"hiveplotlib.Axis(axis_id='{self.axis_id}', start={self.polar_start}, "
            f"end={self.polar_end}, angle={self.angle}, long_name='{self.long_name}')"
        )

    def set_node_placements(
        self,
        placements_df: pd.DataFrame,
        unique_id: Hashable,
    ) -> None:
        """
        Set ``Axis.node_placements`` to a ``pandas.DataFrame`` of node placement information with node metadata.

        Dataframe consists of x cartesian coordinates, y cartesian coordinates, unique node IDs, and polar *rho* values
        (e.g. distance from the origin).

        .. note::
            This is an internal setter method to be called downstream by the ``HivePlot.place_nodes_on_axis()``
            method.

        :param placements_df: dataframe of placement information and other node metadata.
        :param unique_id: column corresponding to node unique IDs.
        :return: ``None``.
        """
        assert "x" in placements_df.columns.to_numpy(), (
            "'x' not in `node_df` column names"
        )
        assert "y" in placements_df.columns.to_numpy(), (
            "'y' not in `node_df` column names"
        )
        assert unique_id in placements_df.columns.to_numpy(), (
            f"'{unique_id}' not in `node_df` column names"
        )
        assert "rho" in placements_df.columns.to_numpy(), (
            "'rho' not in `node_df` column names"
        )

        self.node_placements = placements_df.copy()

        return

    def set_sorting_variable(self, label: Hashable) -> None:
        """
        Set which scalar variable in each ``Node`` instance will be used to place each node on the axis when plotting.

        .. note::
            This is an internal setter method to be called downstream by the ``HivePlot.place_nodes_on_axis()``
            method.

        :param label: which scalar variable in the node data to reference.
        :return: ``None``.
        """
        self.sorting_variable = label

    def set_node_vmin_and_vmax(
        self, vmin: float, vmax: float, inferred_vmin: bool, inferred_vmax: bool
    ) -> None:
        """
        Set the vmin and vmax values used to place nodes on the axis.

        .. note::
            This is an internal setter method to be called downstream by the ``HivePlot.place_nodes_on_axis()``
            method.

        :param vmin: all node scalar values less than ``vmin`` would have been set to ``vmin``
        :param vmax: all node scalar values greater than ``vmax`` would have been set to ``vmax``.
        :param inferred_vmin: whether ``vmin`` value was inferred in ``HivePlot.place_nodes_on_axis()``.
        :param inferred_vmax: whether ``vmax`` value was inferred in ``HivePlot.place_nodes_on_axis()``.
        :return: ``None``.
        """
        self.vmin = vmin
        self.vmax = vmax
        self.inferred_vmin = inferred_vmin
        self.inferred_vmax = inferred_vmax

    def add_metadata(self, metadata: dict) -> None:
        """
        Add metadata to the axis.

        This method will overwrite existing metadata with the same keys.

        :param metadata: dictionary of metadata to add to the axis.
        :return: ``None``.
        """
        self.metadata.update(metadata)
        return
