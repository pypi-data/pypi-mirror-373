# hiveplot.py

"""
Definition of ``BaseHivePlot`` and ``HivePlot`` instances for generating and working with Hive Plots.
"""

import json
import warnings
from copy import deepcopy
from typing import (
    Dict,
    Hashable,
    List,
    Literal,
    Optional,
    Union,
    get_args,
)

import numpy as np
import pandas as pd

from hiveplotlib.axis import Axis
from hiveplotlib.edges import Edges
from hiveplotlib.exceptions import (
    InvalidAxesOrderError,
    InvalidAxisNameError,
    InvalidEdgeKwargHierarchyError,
    InvalidPartitionVariableError,
    InvalidSortingVariableError,
    MissingSortingVariableError,
    RepeatInPartitionAxisNameError,
)
from hiveplotlib.exceptions.hive_plot import InvalidVizBackendError, UnspecifiedTagError
from hiveplotlib.node import (
    Node,
    NodeCollection,
    node_collection_from_node_list,
)
from hiveplotlib.utils import bezier_all, polar2cartesian


def supported_viz_backends():  # noqa: ANN201
    """
    Return the supported visualization back ends for ``hiveplotlib`` hive plots.
    """
    return Literal[
        "bokeh",
        "datashader",
        "holoviews-bokeh",
        "holoviews-matplotlib",
        "matplotlib",
        "plotly",
    ]


SUPPORTED_VIZ_BACKENDS = supported_viz_backends()
"""
The maintained visualization backends supported by ``hiveplotlib``.
"""

EDGE_KWARG_HIERARCHY = Literal[
    "all_edge_kwargs",
    "repeat_edge_kwargs",
    "non_repeat_edge_kwargs",
    "clockwise_edge_kwargs",
    "counterclockwise_edge_kwargs",
]
"""
Options for the hierarchy of edge keyword arguments.
"""


class BaseHivePlot:
    """
    Hive Plots built from combination of ``Axis`` and ``Node`` instances.

    This class is essentially methods for creating and maintaining the nested dictionary attribute ``edges``,
    which holds constructed Bézier curves, edge ids, and matplotlib keyword arguments for various sets of edges to be
    plotted. The nested dictionary structure can be abstracted to the below example.

    .. highlight:: python
    .. code-block:: python

        BaseHivePlot.hive_plot_edges["starting axis"]["ending axis"]["tag"]

    The resulting dictionary value holds the edge information relating to an addition of edges that are tagged as
    "tag," specifically the edges going *FROM* the axis named "starting axis" *TO* the axis named "ending axis." This
    value is in fact another dictionary, meant to hold the discretized Bézier curves (``curves``), the matplotlib
    keyword arguments for plotting (``edge_kwargs``), and the abstracted edge ids (an ``(m, 2) np.ndarray``) between
    which we are drawing Bézier curves (``ids``).
    """

    def __init__(self) -> None:
        """
        Initialize ``HivePlot`` object.
        """
        # keep dictionary of axes, so we can find axes by label
        self.axes = {}

        # keep a NodeCollection instance of node information
        self.nodes = None

        # keep an Edges instance of edge information
        self.edges = None

        # maintain dictionary of node assignments to axes
        # keys will be axes IDs with values being associated dataframes of node placement data
        #  (note, this may not always be a perfect partition of nodes, e.g. repeat axis)
        self.node_assignments = {}

        # maintain dictionary of dictionaries of dictionaries of edge information
        self.hive_plot_edges = {}

        # maintain the largest polar end point from the axes (for plotting)
        self.max_polar_end = None

    def add_axes(self, axes: Union[Axis, List[Axis]]) -> None:
        """
        Add list of ``Axis`` instances to ``axes`` attribute.

        .. note::
            All resulting Axis IDs *must* be unique.

        :param axes: ``Axis`` object(s) to add to ``axes`` attribute.
        :return: ``None``.
        """
        if isinstance(axes, Axis):
            axes = [axes]
        current_ids = list(self.axes.keys())
        new_ids = [axis.axis_id for axis in axes]
        combined_ids = current_ids + new_ids
        assert len(combined_ids) == len(set(combined_ids)), (
            "New specified axis IDs combined with existing IDs led to non-unique IDs. Not adding specified axes."
        )

        for axis in axes:
            self.axes[axis.axis_id] = axis
            self.node_assignments[axis.axis_id] = None

        # update overall largest max polar end point
        self.max_polar_end = max([axis.polar_end for axis in self.axes.values()])

    def add_nodes(
        self, nodes: Union[NodeCollection, List[Node]], check_uniqueness: bool = True
    ) -> None:
        """
        Add ``NodeCollection`` or ``Node`` instances to ``nodes`` attribute.

        :param nodes: ``NodeCollection`` instance or list of ``Node`` instances, will be added to ``nodes`` attribute.
        :param check_uniqueness: whether to formally check for uniqueness.
            WARNING: the only reason to turn this off is if the dataset becomes big enough that this operation becomes
            expensive, and you have already established uniqueness another way (for example, you are pulling data from
            a database and the key in your table is the unique ID). If you add non-unique IDs with
            ``check_uniqueness=False``, we make no promises about output.
        :return: ``None``.
        """
        if not isinstance(nodes, NodeCollection):
            nodes = node_collection_from_node_list(
                node_list=nodes, check_uniqueness=check_uniqueness
            )

        if self.nodes is None:
            self.nodes = nodes
            return

        assert nodes.unique_id_column == self.nodes.unique_id_column, (
            f"Existing NodeCollection unique ID column ({self.nodes.unique_id_column}) is different "
            f"from the provided NodeCollection ({nodes.unique_id_column})"
        )
        self.nodes = NodeCollection(
            data=pd.concat([nodes.data, self.nodes.data]),
            unique_id_column=self.nodes.unique_id_column,
        )

    def add_edges(self, edges: Union[Edges, np.ndarray]) -> None:
        """
        Add edges to ``edges`` attribute.

        :param edges: ``Edges`` instance or 2d array of [from, to] edges, where values correspond to unique node IDs.
        :return: ``None``.
        """
        if not isinstance(edges, Edges):
            edges = Edges(data=edges)

        if self.edges is None:
            self.edges = edges

        else:
            assert edges.from_column_name == self.edges.from_column_name, (
                f"Existing Edges from column name ({self.edges.from_column_name}) is different "
                f"from the provided edges ({edges.from_column_name})"
            )

            assert edges.to_column_name == self.edges.to_column_name, (
                f"Existing Edges to column name ({self.edges.to_column_name}) is different "
                f"from the provided edges ({edges.to_column_name})"
            )
            self.edges.add_edges(data=edges._data)

    def _allocate_nodes_to_axis(self, node_df: pd.DataFrame, axis_id: Hashable) -> None:
        """
        Allocate a set of nodes (dataframe of node info) to a single ``Axis`` (specified by a unique ``axis_id``).

        .. note::
            This is NOT sufficient for plotting nodes, only an underlying setter method called in
            ``BaseHivePlot.place_nodes_on_axis()``.

        :param node_df: dataframe of node ID information to place on specified axis.
        :param axis_id: unique ID of ``Axis`` assigned to ``BaseHivePlot`` instance on which we want to place nodes.
        :return: ``None``.
        """
        self.node_assignments[axis_id] = node_df

    def place_nodes_on_axis(
        self,
        axis_id: Hashable,
        node_df: Optional[pd.DataFrame] = None,
        sorting_feature_to_use: Optional[Hashable] = None,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        unique_ids: None = None,
    ) -> None:
        """
        Set node positions on specific ``Axis``.

        Cartesian coordinates will be normalized to specified ``vmin`` and ``vmax``. Those ``vmin`` and ``vmax``
        values will then be normalized to span the length of the axis when plotted.

        .. note::
            ``unique_ids`` was removed as a parameter in version 0.26.0. Node data must now be provided as a
            ``pandas.DataFrame`` via the ``node_df`` parameter.

        :param axis_id: which axis (as specified by the keys from the ``axes`` attribute) for which to plot nodes.
        :param node_df: dataframe of node information to assign to this axis. If previously set with
            ``BaseHivePlot._allocate_nodes_to_axis()``, this will overwrite those node assignments. If ``None``, method
            will check and confirm there are existing node ID assignments.
        :param sorting_feature_to_use: which feature in the node data to use to align nodes on an axis.
            Default ``None`` uses the feature previously assigned via
            ``BaseHivePlot.axes[axis_id].set_sorting_variable()``.
        :param vmin: all values less than ``vmin`` will be set to ``vmin``. Default ``None`` sets as global minimum of
            feature values for all ``Node`` instances on specified ``Axis``.
        :param vmax: all values greater than ``vmax`` will be set to ``vmax``. Default ``None`` sets as global maximum
            of feature values for all ``Node`` instances on specified ``Axis``.
        :param unique_ids: REMOVED IN VERSION 0.26.0. See note above.
        :raises TypeError: if no-longer supported ``unique_ids`` parameter used.
        :return: ``None``.
        """
        if unique_ids is not None:
            raise TypeError(
                "As of hiveplotlib>=0.26.0, `place_nodes_on_axis() now takes node subsets via the `node_df` parameter, "
                "with support dropped for `unique_ids`. Node dataframe subsetting should be performed on the hive "
                "plot's node dataframe, stored under the hive plot's ``nodes.data`` attribute."
            )
        # ToDo: allow rescaling option before thresholding on min and max values (e.g. put in log scale)

        if node_df is None:
            assert self.node_assignments[axis_id] is not None, (
                f"No existing node data assigned to axis {axis_id}. Please provide `node_df` to place on this axis."
            )
        else:
            self._allocate_nodes_to_axis(node_df=node_df, axis_id=axis_id)

        # assign which data label to use
        if sorting_feature_to_use is not None:
            self.axes[axis_id].set_sorting_variable(label=sorting_feature_to_use)

        else:
            assert self.axes[axis_id].sorting_variable is not None, (
                "Must either specify which feature to use in "
                "`BaseHivePlot.place_nodes_on_axis(feature_to_use=<Hashable>)` "
                "or set the feature directly on the `Axis.set_sorting_variable(label=<Hashable>)`."
            )

        axis = self.axes[axis_id]

        assert axis.sorting_variable is not None, (
            "Must choose a node feature on which to order points with `Axis.set_sorting_variable()`"
        )

        all_node_data = self.node_assignments[axis_id].copy()
        all_vals = all_node_data.loc[:, axis.sorting_variable].astype(float)

        # keep track of whether we inferred either of vmin or vmax
        inferred_vmin = False
        inferred_vmax = False

        if vmin is None:
            vmin = np.min(all_vals)
            inferred_vmin = True
        if vmax is None:
            vmax = np.max(all_vals)
            inferred_vmax = True

        # handle case of one point on an axis but no vmin or vmax specified (put it at the midpoint)
        if all_vals.size == 1 and vmin == vmax:
            vmin -= 1
            vmax += 1
            inferred_vmin = True
            inferred_vmax = True

        # handle case of one unique value on an axis but no vmin or vmax specified (put it at the midpoint)
        if np.unique(all_vals).size == 1 and vmin == vmax:
            vmin -= 1
            vmax += 1
            inferred_vmin = True
            inferred_vmax = True

        # store the vmin and vmax value for future reference
        self.axes[axis_id].set_node_vmin_and_vmax(
            vmin=vmin,
            vmax=vmax,
            inferred_vmin=inferred_vmin,
            inferred_vmax=inferred_vmax,
        )

        # scale values to [vmin, vmax]
        all_vals[all_vals < vmin] = vmin
        all_vals[all_vals > vmax] = vmax

        # normalize to vmin = 0, vmax = 1
        all_vals -= vmin
        all_vals /= vmax - vmin
        # scale to length of axis
        all_vals *= np.abs(axis.polar_end - axis.polar_start)
        # shift to correct starting point which could be off the origin
        all_vals += axis.polar_start

        # translate into cartesian coords
        x_coords, y_coords = polar2cartesian(all_vals, axis.angle)

        all_node_data["x"] = x_coords
        all_node_data["y"] = y_coords
        all_node_data["rho"] = all_vals

        # update pandas dataframe of cartesian coordinate information and polar rho coordinates
        axis.set_node_placements(
            placements_df=all_node_data,
            unique_id=self.nodes.unique_id_column,
        )

        # remove any curves that were previously pointing to this axis
        #  (since they were based on a different alignment of nodes)
        for a0 in list(self.hive_plot_edges.keys()):
            for a1 in list(self.hive_plot_edges[a0].keys()):
                if a0 == axis_id or a1 == axis_id:
                    for k in self.hive_plot_edges[a0][a1]:
                        if "curves" in self.hive_plot_edges[a0][a1][k]:
                            del self.hive_plot_edges[a0][a1][k]["curves"]

    def reset_edges(
        self,
        axis_id_1: Optional[Hashable] = None,
        axis_id_2: Optional[Hashable] = None,
        tag: Optional[Hashable] = None,
        a1_to_a2: bool = True,
        a2_to_a1: bool = True,
    ) -> None:
        """
        Reset ``hive_plot_edges`` attribute and corresponding ``edges.relevant_edges`` (if ``edges`` exists).

        Setting all the parameters to ``None`` deletes any stored connections between axes previously computed. If any
        subset of the parameters is not ``None``, the resulting edges will be deleted:

        If ``axis_id_1``, ``axis_id_2``, and ``tag`` are all specified as *not* ``None``, the implied
        single subset of edges will be deleted. (Note, tags are required to be unique within a specified
        (axis_id_1, axis_id_2) pair.) In this case, the default is to delete all the edges bidirectionally (e.g. going
        ``axis_id_1`` -> ``axis_id_2`` *and* ``axis_id_2`` -> ``axis_id_1``) with the specified ``tag``. To
        only delete edges in one of these directions, see the description of the ``bool`` parameters ``a1_to_a2`` and
        ``a2_to_a1`` below.

        If *only* ``axis_id_1`` and ``axis_id_2`` are provided as not ``None``, then the default is to delete all edge
        subsets bidirectionally between ``axis_id_1`` to ``axis_id_2`` (e.g. going
        ``axis_id_1`` -> ``axis_id_2`` *and* ``axis_id_2`` -> ``axis_id_1``) with the specified ``tag``. To
        only delete edges in one of these directions, see the description of the ``bool`` parameters ``a1_to_a2`` and
        ``a2_to_a1`` below.

        If *only* ``axis_id_1`` is provided as not ``None``, then all edges going *TO* and *FROM* ``axis_id_1`` will be
        deleted. To only delete edges in one of these directions, see the description of the ``bool`` parameters
        ``a1_to_a2`` and ``a2_to_a1`` below.

        :param axis_id_1: specifies edges all coming FROM the axis identified by this unique ID.
        :param axis_id_2: specifies edges all coming TO the axis identified by this unique ID.
        :param tag: tag corresponding to explicit subset of added edges.
        :param a1_to_a2: whether to remove the connections going FROM ``axis_id_1`` TO ``axis_id_2``. Note, if
            ``axis_id_1`` is specified by ``axis_id_2`` is ``None``, then this dictates whether to remove all edges
            going *from* ``axis_id_1``.
        :param a2_to_a1: whether to remove the connections going FROM ``axis_id_2`` TO ``axis_id_1``. Note, if
            ``axis_id_1`` is specified by ``axis_id_2`` is ``None``, then this dictates whether to remove all edges
            going *to* ``axis_id_1``.
        :return: ``None``.
        """
        # all None => reset all edges
        if axis_id_1 is None and axis_id_2 is None and tag is None:
            self.hive_plot_edges = {}
            if self.edges is not None:
                self.edges.relevant_edges = {}

        # all specified => reset just unique tag subset
        elif tag is not None and axis_id_2 is not None and axis_id_1 is not None:
            if a1_to_a2:
                if tag in self.hive_plot_edges[axis_id_1][axis_id_2]:
                    del self.hive_plot_edges[axis_id_1][axis_id_2][tag]
                    if self.edges is not None:
                        self.edges.relevant_edges.setdefault(axis_id_1, {})
                        self.edges.relevant_edges[axis_id_1].setdefault(axis_id_2, {})
                        self.edges.relevant_edges[axis_id_1][axis_id_2][tag] = {}
                else:
                    raise ValueError("Key to delete not found. No edge data deleted.")
            if a2_to_a1:
                if tag in self.hive_plot_edges[axis_id_2][axis_id_1]:
                    del self.hive_plot_edges[axis_id_2][axis_id_1][tag]
                    if self.edges is not None:
                        self.edges.relevant_edges.setdefault(axis_id_2, {})
                        self.edges.relevant_edges[axis_id_2].setdefault(axis_id_1, {})
                        self.edges.relevant_edges[axis_id_2][axis_id_1][tag] = {}
                else:
                    raise ValueError("Key to delete not found. No edge data deleted.")

        # just to and from axes => kill all the connections between the two axes
        elif axis_id_2 is not None and axis_id_1 is not None:
            if a1_to_a2 and axis_id_2 in self.hive_plot_edges[axis_id_1]:
                del self.hive_plot_edges[axis_id_1][axis_id_2]
                if self.edges is not None:
                    self.edges.relevant_edges.setdefault(axis_id_1, {})
                    self.edges.relevant_edges[axis_id_1][axis_id_2] = {}
            if a2_to_a1 and axis_id_1 in self.hive_plot_edges[axis_id_2]:
                del self.hive_plot_edges[axis_id_2][axis_id_1]
                if self.edges is not None:
                    self.edges.relevant_edges.setdefault(axis_id_2, {})
                    self.edges.relevant_edges[axis_id_2][axis_id_1] = {}

        # just one axis => kill all connections coming to / from it
        elif axis_id_1 is not None and axis_id_2 is None:
            # kill "from" connections
            if a1_to_a2 and axis_id_1 in self.hive_plot_edges:
                del self.hive_plot_edges[axis_id_1]
                if self.edges is not None:
                    self.edges.relevant_edges[axis_id_1] = {}
            # kill "to" connections
            if a2_to_a1:
                for a0 in self.hive_plot_edges:
                    if axis_id_1 in self.hive_plot_edges[a0]:
                        del self.hive_plot_edges[a0][axis_id_1]
                        if self.edges is not None:
                            self.edges.relevant_edges.setdefault(a0, {})
                            self.edges.relevant_edges[a0][axis_id_1] = {}

        else:
            raise NotImplementedError(
                "See the docstring for ``BaseHivePlot.reset_edges()`` for more on supported uses."
            )

    def __check_unique_edge_subset_tag(
        self, tag: Hashable, from_axis_id: Hashable, to_axis_id: Hashable
    ) -> None:
        """
        Make sure any ``tag`` specified to represent a subset of added edges is unique in its pair of (from, to) axes.

        Raises ``ValueError`` if ``tag`` is not unique.

        :param tag: unique ID corresponding to an added edge set.
        :param from_axis_id: ID of axis that nodes are coming "from."
        :param to_axis_id: ID of axis that nodes are going "to."
        :return: ``None``.
        """
        if tag in self.hive_plot_edges[from_axis_id][to_axis_id]:
            raise ValueError(
                f"Non-unique tag ({tag}) specified from {from_axis_id} to {to_axis_id}.\n"
                "Please provide edge subset with a new unique tag."
            )

    def _find_unique_tag(
        self, from_axis_id: Hashable, to_axis_id: Hashable, bidirectional: bool = False
    ) -> Hashable:
        """
        Find the first unique, unused ``tag`` value between ``from_axis_id`` and ``to_axis_id``.

        Check by starting at 0 and incrementing up by 1 until the integer is unique.

        :param from_axis_id: ID of axis that nodes are coming "from."
        :param to_axis_id: ID of axis that nodes are going "to."
        :param bidirectional: whether to generate a tag that is unique for *both*
            ``from_axis_id`` -> ``to_axis_id`` AND ``to_axis_id`` -> ``from_axis_id``. Default ``False`` only guarantees
            the former direction.
        :return: ``Hashable`` of resulting unique tag.
        """
        tag_list = list(self.hive_plot_edges[from_axis_id][to_axis_id].keys())
        # if the other direction of edges doesn't exist, then this tag would have to be unique
        if (
            bidirectional
            and to_axis_id in self.hive_plot_edges
            and from_axis_id in self.hive_plot_edges[to_axis_id]
        ):
            tag_list += list(self.hive_plot_edges[to_axis_id][from_axis_id].keys())

        tag = 0
        while True:
            if tag not in tag_list:
                break
            tag += 1

        return tag

    def __store_edge_ids(
        self,
        edge_ids: np.ndarray,
        indices_to_store: list[bool],
        from_axis_id: Hashable,
        to_axis_id: Hashable,
        tag: Optional[Hashable] = None,
        bidirectional: bool = False,
    ) -> Hashable:
        """
        Store edge ids to ``hive_plot_edges`` attribute (e.g. the unique IDs for nodes "from" and "to" for each edge).

        Also store the relevant ``indices_to_store`` in
        ``edges.relevant_indices[from_axis_id][to_axis_id][tag]``.

        :param edge_ids: *all* the node IDs of "from" and "to" nodes (i.e. not yet subset).
        :param indices_to_store: boolean list of indices of ``edge_ids`` to store. Only ``True`` valued indices from
            ``edge_ids`` will be stored.
        :param from_axis_id: ID of axis that nodes are coming "from."
        :param to_axis_id: ID of axis that nodes are going "to."
        :param tag: tag corresponding to subset of specified edges. If ``None`` is provided, the tag will be set as
            the lowest unused integer of the tags specified for this (``from_axis_id``, ``to_axis_id``) pair, starting
            at ``0`` amongst the available tags under ``BaseHivePlot.hive_plot_edges[from_axis_id][to_axis_id]``.
        :param bidirectional: if ``tag`` is ``None``, this boolean value if ``True`` guarantees that the resulting tag
            that will be generated is unique  for *both* ``from_axis_id`` -> ``to_axis_id``
            AND ``to_axis_id`` -> ``from_axis_id``. Default ``False`` only guarantees uniqueness for the former
            direction. Note: edges are still only added for ``from_axis_id`` -> ``to_axis_id``. This parameter exists
            solely for validating whether a newly generated tag must be unique bidirectionally.
        :return: the resulting unique tag.
        """
        from_keys = list(self.hive_plot_edges.keys())
        if from_axis_id not in from_keys:
            self.hive_plot_edges[from_axis_id] = {}
            self.hive_plot_edges[from_axis_id][to_axis_id] = {}

        to_keys = list(self.hive_plot_edges[from_axis_id].keys())
        if to_axis_id not in to_keys:
            self.hive_plot_edges[from_axis_id][to_axis_id] = {}

        # make sure we create a unique integer tag if no tag is specified
        if tag is None:
            tag = self._find_unique_tag(
                from_axis_id=from_axis_id,
                to_axis_id=to_axis_id,
                bidirectional=bidirectional,
            )

        # make sure tag sufficiently unique when specified
        else:
            self.__check_unique_edge_subset_tag(
                tag=tag, from_axis_id=from_axis_id, to_axis_id=to_axis_id
            )

        self.hive_plot_edges[from_axis_id][to_axis_id][tag] = {}

        self.hive_plot_edges[from_axis_id][to_axis_id][tag]["ids"] = edge_ids[
            indices_to_store
        ]

        # also track relevant indices in `edges` attribute, setting up dict structure if not already there
        #  (only if ``edges`` defined)
        if self.edges is not None:
            self.edges.relevant_edges.setdefault(from_axis_id, {})
            self.edges.relevant_edges[from_axis_id].setdefault(to_axis_id, {})
            self.edges.relevant_edges[from_axis_id][to_axis_id].setdefault(tag, {})
            self.edges.relevant_edges[from_axis_id][to_axis_id][tag] = indices_to_store

        return tag

    def add_edge_ids(
        self,
        edges: Union[Edges, np.ndarray],
        axis_id_1: Hashable,
        axis_id_2: Hashable,
        tag: Optional[Hashable] = None,
        a1_to_a2: bool = True,
        a2_to_a1: bool = True,
    ) -> Hashable:
        """
        Find and store the edge IDs relevant to the specified pair of axes.

        Find the subset of network connections that involve nodes on ``axis_id_1`` and ``axis_id_2``.
        looking over the specified ``edges`` compared to the IDs of the ``Node`` instances currently placed on each
        ``Axis``. Edges discovered between the specified two axes (depending on the values specified by ``a1_to_a2`` and
        ``a2_to_a1``, more below) will have the relevant edge IDs stored, with other edges disregarded.

        Generates ``(j, 2)`` and ``(k, 2)`` numpy arrays of ``axis_id_1`` to ``axis_id_2`` connections and ``axis_id_2``
        to ``axis_id_1`` connections (or only 1 of those arrays depending on parameter choices for ``a1_to_a2`` and
        ``a2_to_a1``).

        The resulting arrays of relevant edge IDs (e.g. each row is a [<FROM ID>, <TO ID>] edge) will be stored
        automatically in the ``hive_plot_edges`` attribute, a dictionary of dictionaries of dictionaries of edge
        information, which can later be converted into discretized edges to be plotted in Cartesian space. They are
        stored as ``hive_plot_edges[<source_axis_id>][<sink_axis_id>][<tag>]["ids"]``.

        .. note::
            If no ``tag`` is provided (e.g. default ``None``), one will be automatically generated and returned by
            this method call.

        :param edges: ``Edges`` instance or ``(n, 2)`` array of ``Hashable`` values representing unique IDs of specific
            ``Node`` instances. The first column is the IDs for the "from" nodes and the second column is the IDS for
            the "to" nodes for each connection.
        :param axis_id_1: pointer to first of two ``Axis`` instances in the ``axes`` attribute between which we want to
            find connections.
        :param axis_id_2: pointer to second of two ``Axis`` instances in the ``axes`` attribute between which we want to
            find connections.
        :param tag: tag corresponding to subset of specified edges. If ``None`` is provided, the tag will be set as
            the lowest unused integer starting at ``0`` amongst the available tags under
            ``hive_plot_edges[axis_id_1][axis_id_2]`` and / or
            ``hive_plot_edges[axis_id_2][axis_id_1]``.
        :param a1_to_a2: whether to find the connections going FROM ``axis_id_1`` TO ``axis_id_2``.
        :param a2_to_a1: whether to find the connections going FROM ``axis_id_2`` TO ``axis_id_1``.
        :return: the resulting unique tag. Note, if both ``a1_to_a2`` and ``a2_to_a1`` are ``True`` the resulting
            unique tag returned will be the same for both directions of edges.
        """
        if isinstance(edges, Edges):
            edges = edges.export_edge_array()
        # only need to validate a bidirectional tag if generating it from scratch
        if a1_to_a2 and a2_to_a1 and tag is None:
            bidirectional = True
        elif not a1_to_a2 and not a2_to_a1:
            raise ValueError("One of `a1_to_a2` or `a2_to_a1` must be true.")
        else:
            bidirectional = False
        # axis 1 to axis 2
        if a1_to_a2:
            if self.axes[axis_id_1].node_placements.shape[0] > 0:
                a1_input = np.isin(
                    edges[:, 0],
                    self.axes[axis_id_1]
                    .node_placements.loc[:, self.nodes.unique_id_column]
                    .to_numpy(),
                )
            # empty dataframe => no overlapping IDs
            else:
                a1_input = []
            if self.axes[axis_id_2].node_placements.shape[0] > 0:
                a2_output = np.isin(
                    edges[:, 1],
                    self.axes[axis_id_2]
                    .node_placements.loc[:, self.nodes.unique_id_column]
                    .to_numpy(),
                )
            else:
                a2_output = []
            a1_to_a2_indices = np.logical_and(a1_input, a2_output)
            new_tag = self.__store_edge_ids(
                edge_ids=edges,
                indices_to_store=a1_to_a2_indices,
                from_axis_id=axis_id_1,
                to_axis_id=axis_id_2,
                tag=tag,
                bidirectional=bidirectional,
            )

        # axis 2 to axis 1
        if a2_to_a1:
            if self.axes[axis_id_1].node_placements.shape[0] > 0:
                a1_output = np.isin(
                    edges[:, 1],
                    self.axes[axis_id_1]
                    .node_placements.loc[:, self.nodes.unique_id_column]
                    .to_numpy(),
                )
            else:
                a1_output = []
            if self.axes[axis_id_2].node_placements.shape[0] > 0:
                a2_input = np.isin(
                    edges[:, 0],
                    self.axes[axis_id_2]
                    .node_placements.loc[:, self.nodes.unique_id_column]
                    .to_numpy(),
                )
            else:
                a2_input = []
            a2_to_a1_indices = np.logical_and(a2_input, a1_output)
            # if doing both, be sure to supply the same tag
            if bidirectional:
                tag = new_tag
            new_tag = self.__store_edge_ids(
                edge_ids=edges,
                indices_to_store=a2_to_a1_indices,
                from_axis_id=axis_id_2,
                to_axis_id=axis_id_1,
                tag=tag,
            )

        return new_tag

    def add_edge_curves_between_axes(
        self,
        axis_id_1: Hashable,
        axis_id_2: Hashable,
        tag: Optional[Hashable] = None,
        a1_to_a2: bool = True,
        a2_to_a1: bool = True,
        num_steps: int = 100,
        short_arc: bool = True,
        control_rho_scale: float = 1,
        control_angle_shift: float = 0,
    ) -> None:
        """
        Construct discretized edge curves between two axes of a Hive Plot.

        .. note::
            One must run the ``add_edge_ids()`` method first for the two axes of interest.

        Resulting discretized Bézier curves will be stored as an ``(n, 2) numpy.ndarray`` of multiple sampled curves
        where the first column is x position and the second column is y position in Cartesian coordinates.

        .. note::
            Although each curve is represented by a ``(num_steps, 2)`` array, all the curves are stored curves in a
            single collective ``numpy.ndarray`` separated by rows of ``[np.nan, np.nan]`` between each discretized
            curve. This allows ``matplotlib`` to accept a single array when plotting lines via ``plt.plot()``, which
            speeds up plotting later.

        This output will be stored in ``hive_plot_edges[axis_id_1][axis_id_2][tag]["curves"]``.

        :param axis_id_1: pointer to first of two ``Axis`` instances in the ``axes`` attribute between which we want to
            find connections.
        :param axis_id_2: pointer to second of two ``Axis`` instances in the ``axes`` attribute between which we want to
            find connections.
        :param tag: unique ID specifying which subset of edges specified by their IDs to construct
            (e.g. ``hive_plot_edges[axis_id_1][axis_id_2][tag]["ids"]``).
            Note, if no tag is specified (e.g. ``tag=None``), it is presumed there is only one tag for the specified
            set of axes to look over, which can be inferred. If no tag is specified and there are multiple tags to
            choose from, a ``ValueError`` will be raised.
        :param a1_to_a2: whether to build out the edges going FROM ``axis_id_1`` TO ``axis_id_2``.
        :param a2_to_a1: whether to build out the edges going FROM ``axis_id_2`` TO ``axis_id_1``.
        :param num_steps: number of points sampled along a given Bézier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (``True``) or longer angle arc (``False``).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default ``True``.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (``short_arc=False``). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :param control_rho_scale: how much to multiply the distance of the control point for each edge to / from the
            origin. Default ``1`` sets the control rho for each edge as the mean rho value for each pair of nodes being
            connected by that edge. A value greater than 1 will pull the resulting edges further away from the origin,
            making edges more convex, while a value between 0 and 1 will pull the resulting edges closer to the origin,
            making edges more concave. Note, this affects edges further from the origin by larger magnitudes than edges
            closer to the origin.
        :param control_angle_shift: how far to rotate the control point for each edge around the origin. Default
            ``0`` sets the control angle for each edge as the mean angle for each pair of nodes being connected by
            that edge. A positive value will pull the resulting edges further counterclockwise, while a negative
            value will pull the resulting edges further clockwise.
        :return: ``None``.
        """
        if tag is None:
            a1_to_a2_failure = False
            a2_to_a1_failure = False
            if a1_to_a2:
                assert (
                    len(list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())) > 0
                ), (
                    "No edges specified to construct. Be sure to run the `add_edge_ids()` method first."
                )

                a1_to_a2_tag = list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())[
                    0
                ]

                if len(list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())) > 1:
                    a1_to_a2_failure = True

            if a2_to_a1:
                assert (
                    len(list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())) > 0
                ), (
                    "No edges specified to construct. Be sure to run the `add_edge_ids()` method first."
                )

                a2_to_a1_tag = list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())[
                    0
                ]

                if len(list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())) > 1:
                    a2_to_a1_failure = True

            if a1_to_a2_failure and a2_to_a1_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle both `a1_to_a2=True` and `a2_to_a1=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_2} -> {axis_id_1: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}}\n"
                    f"{axis_id_2} -> {axis_id_1: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}}"
                )

            if a1_to_a2_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle `a1_to_a2=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_1} -> {axis_id_2: {list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())}}"
                )
            if a2_to_a1_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle `a2_to_a1=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_2} -> {axis_id_1: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}}"
                )

        else:
            a1_to_a2_tag = tag
            a2_to_a1_tag = tag

        all_connections = []
        direction = []
        if a1_to_a2:
            try:
                ids = self.hive_plot_edges[axis_id_1][axis_id_2][a1_to_a2_tag]["ids"]
                temp_connections = ids.copy().astype("O")
                all_connections.append(temp_connections)
                direction.append("a1_to_a2")
            except KeyError as ke:
                raise KeyError(
                    f"`self.edges[{axis_id_1}][{axis_id_2}][{a1_to_a2_tag}]['ids']` does not appear to exist. "
                    "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                ) from ke
        if a2_to_a1:
            try:
                ids = self.hive_plot_edges[axis_id_2][axis_id_1][a2_to_a1_tag]["ids"]
                temp_connections = ids.copy().astype("O")
                all_connections.append(temp_connections)
                direction.append("a2_to_a1")
            except KeyError as ke:
                raise KeyError(
                    f"`self.edges[{axis_id_2}][{axis_id_1}][{a2_to_a1_tag}]['ids']` does not appear to exist. "
                    "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                ) from ke

        if len(all_connections) == 0:
            raise ValueError("One of `a1_to_a2` or `a2_to_a1` must be true.")

        for connections, edge_direction in zip(
            all_connections,
            direction,
        ):
            # left join the flattened start and stop values array with the cartesian and polar node locations
            #  Note: sorting behavior is not cooperating, so needed a trivial np.arange to re-sort at end
            #   (dropped before using `out`)
            if edge_direction == "a1_to_a2":
                start_axis = axis_id_1
                stop_axis = axis_id_2
            elif edge_direction == "a2_to_a1":
                start_axis = axis_id_2
                stop_axis = axis_id_1

            start = (
                pd.DataFrame(np.c_[connections[:, 0], np.arange(connections.shape[0])])
                .merge(
                    self.axes[start_axis].node_placements,
                    left_on=0,
                    right_on=self.nodes.unique_id_column,
                    how="left",
                )
                .sort_values(1)
                .loc[:, ["x", "y", "rho"]]
            )

            stop = (
                pd.DataFrame(np.c_[connections[:, 1], np.arange(connections.shape[0])])
                .merge(
                    self.axes[stop_axis].node_placements,
                    left_on=0,
                    right_on=self.nodes.unique_id_column,
                    how="left",
                )
                .sort_values(1)
                .loc[:, ["x", "y", "rho"]]
            )

            start_arr = start.loc[:, ["x", "y"]].to_numpy()
            end_arr = stop.loc[:, ["x", "y"]].to_numpy()

            # we only want one rho for the start, stop pair (using the mean rho)
            control_rho = (
                start.loc[:, "rho"].to_numpy() + stop.loc[:, "rho"].to_numpy()
            ) / 2

            # all interactions between same two axes, so only one angle
            angles = [self.axes[axis_id_1].angle, self.axes[axis_id_2].angle]
            angle_diff = angles[1] - angles[0]

            # make sure we take the short arc if requested
            if short_arc:
                if np.abs(angle_diff) > 180:
                    # flip the direction in this case and angle between is now "360 minus"
                    control_angle = (
                        angles[0]
                        + -1 * np.sign(angle_diff) * (360 - np.abs(angle_diff)) / 2
                    )
                else:
                    control_angle = angles[0] + angle_diff / 2
            # long arc
            elif np.abs(angle_diff) <= 180:
                # flip the direction in this case and angle between is now "360 minus"
                control_angle = (
                    angles[0]
                    + -1 * np.sign(angle_diff) * (360 - np.abs(angle_diff)) / 2
                )
            else:
                control_angle = angles[0] + angle_diff / 2

            # use calculated rho and angle augmented with any user-requested shifts
            control_cartesian = polar2cartesian(
                rho=control_rho * control_rho_scale,
                phi=control_angle + control_angle_shift,
            )
            bezier_output = np.column_stack(
                [
                    bezier_all(
                        start_arr=start_arr[:, i],
                        end_arr=end_arr[:, i],
                        control_arr=control_cartesian[i],
                        num_steps=num_steps,
                    )
                    for i in range(2)
                ]
            )

            # put `np.nan` spacers in
            bezier_output = np.insert(
                arr=bezier_output,
                obj=np.arange(bezier_output.shape[0], step=num_steps) + num_steps,
                values=np.nan,
                axis=0,
            )

            # store the output in the right place(s)
            if edge_direction == "a1_to_a2":
                self.hive_plot_edges[axis_id_1][axis_id_2][a1_to_a2_tag]["curves"] = (
                    bezier_output
                )

            elif edge_direction == "a2_to_a1":
                self.hive_plot_edges[axis_id_2][axis_id_1][a2_to_a1_tag]["curves"] = (
                    bezier_output
                )

    def construct_curves(
        self,
        num_steps: int = 100,
        short_arc: bool = True,
        control_rho_scale: float = 1,
        control_angle_shift: float = 0,
    ) -> None:
        """
        Construct Bézier curves for any connections for which we've specified the edges to draw.

        (e.g. ``hive_plot_edges[axis_0][axis_1][<tag>]["ids"]`` is non-empty but
        ``hive_plot_edges[axis_0][axis_1][<tag>]["curves"]`` does not yet exist).

        .. note::
            Checks all <tag> values between axes.

        :param num_steps: number of points sampled along a given Bézier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (``True``) or longer angle arc (``False``).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default ``True``.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (``short_arc=False``). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :param control_rho_scale: how much to multiply the distance of the control point for each edge to / from the
            origin. Default ``1`` sets the control rho for each edge as the mean rho value for each pair of nodes being
            connected by that edge. A value greater than 1 will pull the resulting edges further away from the origin,
            making edges more convex, while a value between 0 and 1 will pull the resulting edges closer to the origin,
            making edges more concave. Note, this affects edges further from the origin by larger magnitudes than edges
            closer to the origin.
        :param control_angle_shift: how far to rotate the control point for each edge around the origin. Default
            ``0`` sets the control angle for each edge as the mean angle for each pair of nodes being connected by
            that edge. A positive value will pull the resulting edges further counterclockwise, while a negative
            value will pull the resulting edges further clockwise.
        :return: ``None``.
        """
        for a0 in list(self.hive_plot_edges.keys()):
            for a1 in list(self.hive_plot_edges[a0].keys()):
                for tag in list(self.hive_plot_edges[a0][a1].keys()):
                    if (
                        "ids" in self.hive_plot_edges[a0][a1][tag]
                        and "curves" not in self.hive_plot_edges[a0][a1][tag]
                    ):
                        self.add_edge_curves_between_axes(
                            axis_id_1=a0,
                            axis_id_2=a1,
                            a2_to_a1=False,
                            tag=tag,
                            num_steps=num_steps,
                            short_arc=short_arc,
                            control_rho_scale=control_rho_scale,
                            control_angle_shift=control_angle_shift,
                        )

    def add_edge_kwargs(
        self,
        axis_id_1: Hashable,
        axis_id_2: Hashable,
        tag: Optional[Hashable] = None,
        a1_to_a2: bool = True,
        a2_to_a1: bool = True,
        reset_existing_kwargs: bool = False,
        overwrite_existing_kwargs: bool = True,
        warn_on_no_edges: bool = True,
        **edge_kwargs,
    ) -> None:
        """
        Add edge kwargs to the constructed ``hive_plot_edges`` attribute between two axes of a Hive Plot.

        For a given set of edges for which edge kwargs were already set, any redundant edge kwargs specified by this
        method call will overwrite the previously set kwargs.

        Expected to have found edge IDs between the two axes before calling this method, which can be done either
        by calling the ``connect_axes()`` method or the lower-level ``add_edge_ids()`` method for the two
        axes of interest. A warning will be raised if no edges exist between the two axes and ``warn_on_no_edges=True``.

        Resulting kwargs will be stored as a dict. This output will be stored in
        ``hive_plot_edges[axis_id_1][axis_id_2][tag]["edge_kwargs"]``.

        .. note::
            There is special handling in here for when the two provided axes have names ``"<axis_name>"`` and
            ``"<axis_name>_repeat"``. This is for use with ``hiveplotlib.hive_plot_n_axes()``, which when creating
            repeat axes always names the repeated one ``"<axis_name>_repeat"``. By definition, the edges between an axis
            and its repeat are the same, and therefore edges between these two axes should *only* be plotted in one
            direction. If one is running this method on a ``Hiveplot`` instance from ``hiveplotlib.hive_plot_n_axes()``
            though, a warning of a lack of edges in both directions for repeat edges is not productive, so we formally
            catch this case.

        :param axis_id_1: Hashable pointer to the first ``Axis`` instance in the ``axes`` attribute to which we want to
            add plotting kwargs.
        :param axis_id_2: Hashable pointer to the second ``Axis`` instance in the ``axes`` attribute to which we want to
            add plotting kwargs.
        :param tag: which subset of curves to modify kwargs for.
            Note, if no tag is specified (e.g. ``tag=None``), it is presumed there is only one tag for the specified
            set of axes to look over and that will be inferred. If no tag is specified and there are multiple tags to
            choose from, a ``ValueError`` will be raised.
        :param a1_to_a2: whether to add kwargs for connections going FROM ``axis_id_1`` TO ``axis_id_2``.
        :param a2_to_a1: whether to add kwargs for connections going FROM ``axis_id_2`` TO ``axis_id_1``.
        :param reset_existing_kwargs: whether to remove all existing edge kwargs before adding provided ``edge_kwargs``
            for the edges specified by other parameters, default False leaves existing edge kwargs unchanged.
        :param overwrite_existing_kwargs: whether to overwrite existing edge kwargs if provided again, default  ``True``
            overwrites already-provided edge kwargs with the new value(s) in ``edge_kwargs``.
        :param warn_on_no_edges: whether to warn if adding kwargs for edges that don't exist. Default ``True``.
        :param edge_kwargs: additional ``matplotlib`` keyword arguments that will be applied to the specified edges.
        :return: ``None``.
        """
        a1_to_a2_tag = None
        a2_to_a1_tag = None

        if tag is None:
            a1_to_a2_failure = False
            a2_to_a1_failure = False

            # special warning if repeat axes have no edges between each other
            if (
                a1_to_a2
                and a2_to_a1
                and str(axis_id_2).removesuffix("_repeat")
                == str(axis_id_1).removesuffix("_repeat")
            ):
                repeat_edges_defined = False
                if (
                    axis_id_1 in self.hive_plot_edges
                    and axis_id_2 in self.hive_plot_edges[axis_id_1]
                    and len(list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())) > 0
                ):
                    repeat_edges_defined = True
                if (
                    axis_id_2 in self.hive_plot_edges
                    and axis_id_1 in self.hive_plot_edges[axis_id_2]
                    and len(list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())) > 0
                ):
                    repeat_edges_defined = True
                if not repeat_edges_defined and warn_on_no_edges:
                    warnings.warn(
                        f"Repeat axes {axis_id_1} and {axis_id_2} have no edges."
                        "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                        "first.",
                        stacklevel=2,
                    )
            if a1_to_a2:
                if axis_id_1 in self.hive_plot_edges:
                    if axis_id_2 not in self.hive_plot_edges[axis_id_1]:
                        # special handling for the "_repeat" axis
                        #  we check and warn with respect to repeat axes above
                        if (
                            str(axis_id_2).removesuffix("_repeat")
                            != str(axis_id_1).removesuffix("_repeat")
                            and warn_on_no_edges
                        ):
                            warnings.warn(
                                f"No edges exist between axes {axis_id_1} -> {axis_id_2}."
                                "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                                "first.",
                                stacklevel=2,
                            )
                        a1_to_a2 = False
                    elif (
                        len(list(self.hive_plot_edges[axis_id_1][axis_id_2].keys()))
                        == 0
                    ) and warn_on_no_edges:
                        warnings.warn(
                            f"No edges exist between axes {axis_id_1} -> {axis_id_2}."
                            "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                            "first.",
                            stacklevel=2,
                        )
                        a1_to_a2 = False

                    else:
                        a1_to_a2_tag = list(
                            self.hive_plot_edges[axis_id_1][axis_id_2].keys()
                        )[0]

                        if (
                            len(list(self.hive_plot_edges[axis_id_1][axis_id_2].keys()))
                            > 1
                        ):
                            a1_to_a2_failure = True
                else:
                    if (
                        str(axis_id_2).removesuffix("_repeat")
                        != str(axis_id_1).removesuffix("_repeat")
                        and warn_on_no_edges
                    ):
                        warnings.warn(
                            f"No edges exist between axes {axis_id_1} -> {axis_id_2}."
                            "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                            "first.",
                            stacklevel=2,
                        )
                    a1_to_a2 = False

            if a2_to_a1:
                if axis_id_2 in self.hive_plot_edges:
                    if axis_id_1 not in self.hive_plot_edges[axis_id_2]:
                        # special handling for the "_repeat" axis
                        #  we check and warn with respect to repeat axes above
                        if (
                            str(axis_id_2).removesuffix("_repeat")
                            != str(axis_id_1).removesuffix("_repeat")
                            and warn_on_no_edges
                        ):
                            warnings.warn(
                                f"No edges exist between axes {axis_id_2} -> {axis_id_1}."
                                "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                                "first.",
                                stacklevel=2,
                            )
                        a2_to_a1 = False
                    elif (
                        len(list(self.hive_plot_edges[axis_id_2][axis_id_1].keys()))
                        == 0
                    ) and warn_on_no_edges:
                        warnings.warn(
                            f"No edges exist between axes {axis_id_2} -> {axis_id_1}."
                            "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                            "first.",
                            stacklevel=2,
                        )
                        a2_to_a1 = False

                    else:
                        a2_to_a1_tag = list(
                            self.hive_plot_edges[axis_id_2][axis_id_1].keys()
                        )[0]

                        if (
                            len(list(self.hive_plot_edges[axis_id_2][axis_id_1].keys()))
                            > 1
                        ):
                            a2_to_a1_failure = True
                else:
                    if (
                        str(axis_id_2).removesuffix("_repeat")
                        != str(axis_id_1).removesuffix("_repeat")
                        and warn_on_no_edges
                    ):
                        warnings.warn(
                            f"No edges exist between axes {axis_id_2} -> {axis_id_1}."
                            "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                            "first.",
                            stacklevel=2,
                        )
                    a2_to_a1 = False

            if a1_to_a2_failure and a2_to_a1_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle both `a1_to_a2=True` and `a2_to_a1=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_2} -> {axis_id_1}: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}\n"
                    f"{axis_id_2} -> {axis_id_1}: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}"
                )
            if a1_to_a2_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle `a1_to_a2=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_1} -> {axis_id_2}: {list(self.hive_plot_edges[axis_id_1][axis_id_2].keys())}"
                )
            if a2_to_a1_failure:
                raise ValueError(
                    "Must specify precise `tag` to handle `a2_to_a1=True` here. "
                    "The current tags for the specified axes are:\n"
                    f"{axis_id_2} -> {axis_id_1}: {list(self.hive_plot_edges[axis_id_2][axis_id_1].keys())}"
                )

        else:
            a1_to_a2_tag = tag
            a2_to_a1_tag = tag

        axes = []
        tags = []
        for direction, axis_ids, t in zip(
            [a1_to_a2, a2_to_a1],
            [[axis_id_1, axis_id_2], [axis_id_2, axis_id_1]],
            [a1_to_a2_tag, a2_to_a1_tag],
        ):
            if direction:
                if axis_ids[0] not in self.hive_plot_edges:
                    self.hive_plot_edges[axis_ids[0]] = {}
                if axis_ids[1] not in self.hive_plot_edges[axis_ids[0]]:
                    self.hive_plot_edges[axis_ids[0]][axis_ids[1]] = {}
                if t not in self.hive_plot_edges[axis_ids[0]][axis_ids[1]]:
                    self.hive_plot_edges[axis_ids[0]][axis_ids[1]][t] = {}
                if (
                    "ids" not in self.hive_plot_edges[axis_ids[0]][axis_ids[1]][t]
                    and warn_on_no_edges
                ):
                    warnings.warn(
                        f"No edges exist between axes {axis_ids[0]} -> {axis_ids[1]} for tag {t}. "
                        "Be sure to run the `connect_axes()` method or the `add_edge_ids()` method "
                        "first.",
                        stacklevel=2,
                    )
                # add kwargs downstream no matter what if asking for that direction
                axes.append([axis_ids[0], axis_ids[1]])
                tags.append(t)
        # store the kwargs
        for [a1, a2], t in zip(axes, tags):
            if (
                reset_existing_kwargs
                and "edge_kwargs" in self.hive_plot_edges[a1][a2][t]
            ):
                self.hive_plot_edges[a1][a2][t]["edge_kwargs"] = {}
            # being sure to include existing kwargs unless requesting to overwrite them
            if "edge_kwargs" in self.hive_plot_edges[a1][a2][t]:
                if overwrite_existing_kwargs:
                    # new edges take priority
                    self.hive_plot_edges[a1][a2][t]["edge_kwargs"] |= edge_kwargs
                else:
                    # original edges take priority
                    self.hive_plot_edges[a1][a2][t]["edge_kwargs"] = (
                        edge_kwargs | self.hive_plot_edges[a1][a2][t]["edge_kwargs"]
                    )
            else:
                self.hive_plot_edges[a1][a2][t]["edge_kwargs"] = edge_kwargs

    def connect_axes(
        self,
        edges: Union[Edges, np.ndarray],
        axis_id_1: Hashable,
        axis_id_2: Hashable,
        tag: Optional[Hashable] = None,
        a1_to_a2: bool = True,
        a2_to_a1: bool = True,
        num_steps: int = 100,
        short_arc: bool = True,
        control_rho_scale: float = 1,
        control_angle_shift: float = 0,
        reset_existing_kwargs: bool = False,
        overwrite_existing_kwargs: bool = True,
        warn_on_no_edges: bool = True,
        **edge_kwargs,
    ) -> Hashable:
        """
        Construct all the curves and set all the curve kwargs between ``axis_id_1`` and ``axis_id_2``.

        Based on the specified ``edges`` parameter, build out the resulting Bézier curves, and set any kwargs for those
        edges for later visualization.

        The curves will be tracked by a unique ``tag``, and the resulting constructions will be stored in
        ``hive_plot_edges[axis_id_1][axis_id_2][tag]`` if ``a1_to_a2`` is ``True`` and
        ``hive_plot_edges[axis_id_2][axis_id_1][tag]`` if ``a2_to_a1`` is ``True``.

        .. note::
            If trying to draw different subsets of edges with different kwargs, one can run this method multiple times
            with different subsets of the entire edges array, providing unique ``tag`` values with each subset of
            ``edges``, and specifying different ``edge_kwargs`` each time. The resulting Hive Plot would be
            plotted showing each set of edges styled with each set of unique kwargs.

        .. note::
            You can choose to construct edges in only one of either directions by specifying `a1_to_a2` or `a2_to_a1`
            as False (both are True by default).

        :param edges: ``hiveplotlib.Edges`` instance or ``(n, 2)`` array of ``Hashable`` values representing pointers to
            specific ``Node`` instances. If providing an array input, the first column is the "from" and the second
            column is the "to" for each connection.
        :param axis_id_1: Hashable pointer to the first ``Axis`` instance in the ``axes`` attribute we want to find
            connections between.
        :param axis_id_2: Hashable pointer to the second ``Axis`` instance in the ``axes`` attribute we want to find
            connections between.
        :param tag: tag corresponding to specified ``edges``. If ``None`` is provided, the tag will be set as
            the lowest unused integer starting at ``0`` amongst the available tags under
            ``hive_plot_edges[from_axis_id][to_axis_id]`` and / or
            ``hive_plot_edges[to_axis_id][from_axis_id]``.
        :param a1_to_a2: whether to find and build the connections going FROM ``axis_id_1`` TO ``axis_id_2``.
        :param a2_to_a1: whether to find and build the connections going FROM ``axis_id_2`` TO ``axis_id_1``.
        :param num_steps: number of points sampled along a given Bézier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (``True``) or longer angle arc (``False``).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default ``True``.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (``short_arc=False``). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :param control_rho_scale: how much to multiply the distance of the control point for each edge to / from the
            origin. Default ``1`` sets the control rho for each edge as the mean rho value for each pair of nodes being
            connected by that edge. A value greater than 1 will pull the resulting edges further away from the origin,
            making edges more convex, while a value between 0 and 1 will pull the resulting edges closer to the origin,
            making edges more concave. Note, this affects edges further from the origin by larger magnitudes than edges
            closer to the origin.
        :param control_angle_shift: how far to rotate the control point for each edge around the origin. Default
            ``0`` sets the control angle for each edge as the mean angle for each pair of nodes being connected by
            that edge. A positive value will pull the resulting edges further counterclockwise, while a negative
            value will pull the resulting edges further clockwise.
        :param edge_kwargs: additional ``matplotlib`` params that will be applied to the related edges.
        :param reset_existing_kwargs: whether to remove all existing edge kwargs before adding provided ``edge_kwargs``
            for the edges specified by other parameters, default False leaves existing edge kwargs unchanged.
        :param overwrite_existing_kwargs: whether to overwrite existing edge kwargs if provided again, default  ``True``
            overwrites already-provided edge kwargs with the new value(s) in ``edge_kwargs``.
        :param warn_on_no_edges: whether to warn if adding kwargs for edges that don't exist. Default ``True``.
        :return: ``Hashable`` tag that identifies the generated curves and kwargs.
        """
        # if `tag` is `None`, will be relevant to store the new tag, otherwise `new_tag` will just be the same as `tag`
        new_tag = self.add_edge_ids(
            edges=edges,
            tag=tag,
            axis_id_1=axis_id_1,
            axis_id_2=axis_id_2,
            a1_to_a2=a1_to_a2,
            a2_to_a1=a2_to_a1,
        )

        self.add_edge_curves_between_axes(
            axis_id_1=axis_id_1,
            axis_id_2=axis_id_2,
            tag=new_tag,
            a1_to_a2=a1_to_a2,
            a2_to_a1=a2_to_a1,
            num_steps=num_steps,
            short_arc=short_arc,
            control_rho_scale=control_rho_scale,
            control_angle_shift=control_angle_shift,
        )

        self.add_edge_kwargs(
            axis_id_1=axis_id_1,
            axis_id_2=axis_id_2,
            tag=new_tag,
            a1_to_a2=a1_to_a2,
            a2_to_a1=a2_to_a1,
            overwrite_existing_kwargs=overwrite_existing_kwargs,
            reset_existing_kwargs=reset_existing_kwargs,
            warn_on_no_edges=warn_on_no_edges,
            **edge_kwargs,
        )

        return new_tag

    def copy(self):  # noqa: ANN201
        """
        Return a copy of the instance.

        :return: copy of the instance.
        """
        return deepcopy(self)

    def to_json(self) -> str:
        """
        Return the information from the axes, nodes, and edges in Cartesian space as a serialized JSON string.

        This allows users to visualize hive plots with arbitrary libraries, even outside of python.

        The dictionary structure of the resulting JSON will consist of two top-level keys:

        "axes" - contains the information for plotting each axis, plus the nodes on each axis in Cartesian space.

        "edges" - contains the information for plotting the discretized edges in Cartesian space, plus the corresponding
        *to* and *from* IDs that go with each edge, as well as any kwargs that were set for plotting each set of edges.

        :return: JSON output of axis, node, and edge information.
        """
        # axis endpoints and node placements (both in Cartesian space).
        axis_node_dict = {}

        for axis in self.axes:
            # endpoints of axis in Cartesian space
            start, end = self.axes[axis].start, self.axes[axis].end

            temp_dict = {
                "start": start,
                "end": end,
                "nodes": self.axes[axis]
                .node_placements.loc[:, [self.nodes.unique_id_column, "x", "y"]]
                .rename(columns={self.nodes.unique_id_column: "unique_id"})
                .to_dict(orient="list"),
            }
            axis_node_dict[axis] = temp_dict

        edge_info = deepcopy(self.hive_plot_edges)

        # edge ids, discretized curves (in Cartesian space), and kwargs
        for e1 in edge_info:
            for e2 in edge_info[e1]:
                for tag in edge_info[e1][e2]:
                    for i in ["ids", "curves"]:
                        # curves have nan values, must revise to `None` then coax to list
                        if i == "curves":
                            arr = edge_info[e1][e2][tag][i]
                            split_arrays = np.split(
                                arr, np.where(np.isnan(arr[:, 0]))[0]
                            )
                            # be sure to drop the extra array at the end that is just a NaN value
                            split_arrays_str = [
                                arr[~np.isnan(arr[:, 0]), :].astype("O")
                                for arr in split_arrays
                            ][:-1]
                            split_arrays_list = [
                                arr.tolist() for arr in split_arrays_str
                            ]
                            edge_info[e1][e2][tag][i] = split_arrays_list
                        # ids don't have nan values, can be converted to list right away
                        elif i == "ids":
                            edge_info[e1][e2][tag][i] = edge_info[e1][e2][tag][
                                i
                            ].tolist()

        collated_output = {"axes": axis_node_dict, "edges": edge_info}

        return json.dumps(collated_output)


class HivePlot(BaseHivePlot):
    """
    Hive plot instantiation from nodes, edges, a provided partition variable, and sorting variable(s).

    Axes will be created with names corresponding to the unique names in the data specified by ``partition_variable``.

    Nodes must be provided as a :py:class:`hiveplotlib.NodeCollection` instance, and edges must be provided as an
    :py:class:`hiveplotlib.Edges` instance.

    .. note::
        Any provided ``axis_kwargs`` will be applied *after* first initializing the hive plot axes according to the
        ``partition_variable``, ``sorting_variables``, ``repeat_axes``, ``axes_order``, ``rotation``, and
        ``angle_between_repeat_axes`` parameter values.

        By default, a repeat axis ``<axis_name>_repeat`` that has the same sorting variable will match the size,
        labeling, and node positioning of the original ``<axis_name>`` in the resulting hive plot unless the user
        explicitly changes this in initialization. To change this, users can provide ``<axis_name>_repeat`` keyword
        arguments to the ``axis_kwargs`` parameter on initialization or modify the repeat axis later with the
        :py:meth:`hiveplotlib.HivePlot.update_axis()` method.

        If the repeat axis has a different sorting variable, then by default, it will infer the ``vmin`` and ``vmax``
        values to place the nodes spanning the full extent of the resulting axis.

        If a list of ``axes_order`` names are provided *and* one of the names in the provided list is ``None``, then all
        remaining values unspecified in the provided list that are in the current partition as specified by
        ``partition_variable`` will be collapsed onto a single axis. This is particularly useful when the partition
        variable has more than 3 values. To change the name of the collapsed group in the final hive plot visualization,
        see the ``collapsed_group_axis_name`` parameter.

    :param nodes: node data to turn into a hive plot.
    :param edges: edge data corresponding to provided ``nodes`` to turn into a hive plot. If providing a
        ``numpy.ndarray`` of edge data, must be provided as (from, to) pairs. Note, providing an array input does not
        support the inclusion of edge metadata, whereas the ``Edges`` instance input does.
    :param partition_variable: which node variable to use to partition the nodes into separate axes. Partitioning will
        be done by unique values.
    :param sorting_variables: which node variable to use to sort / place the nodes on each axis. Providing a single
        value uses the same variable for each axis. Alternatively, providing a dictionary of keys as the unique values
        from ``partition_variable`` column data and values being the corresponding sorting variable to use for that
        axis. Note when providing a dictionary input, _all_ keys created by the provided ``partition_variable`` must be
        specified (otherwise a ``MissingSortingVariableError`` will be raised).
    :param backend: which visualization backend to use when plotting with the ``plot()`` method.
    :param repeat_axes: unique values from ``partition_variable`` column data for which to create adjacent repeat axes.
        Repeat axes can be turned on for *all* unique values by setting this parameter to ``True``. Default ``False``
        sets no repeat axes.
    :param axes_order: order in which to place axes on the hive plot. Names must correspond to the unique values in
        node data specified by ``partition_variable``. If a list of ``axes_order`` names are provided *and* one of the
        names in the provided list is ``None``, then all remaining values unspecified in the provided list that are in
        the current partition as specified by ``partition_variable`` will be collapsed onto a single axis. This is
        particularly useful when the partition variable has more than 3 values. To change the name of the collapsed
        group in the final hive plot visualization, see the ``collapsed_group_axis_name`` parameter. Default ``None``
        uses the order in the ``pandas`` groupby object stored in the resulting ``partition`` attribute.
    :param rotation: angle (measured in degrees) to rotate *every* axis counterclockwise off of the default value.
        (By default, axes are evenly spaced in polar coordinates, with the first axis drawn at an angle of 0 degrees.)
    :param angle_between_repeat_axes: angle (measured in degrees) to use between repeat axes.
    :param axis_kwargs: nested dictionaries of specific kwargs to update axes. Keys should be unique values from
        ``partition_variable`` column data. Values should be dictionaries corresponding to the parameters in
        :py:meth:`hiveplotlib.HivePlot.update_axis()`.
    :param all_edge_kwargs: additional keyword arguments for plotting all edges. Default ``None`` makes no additional
        modifications when plotting edges.
    :param clockwise_edge_kwargs: additional keyword arguments for plotting edges going clockwise. Default ``None``
        makes no additional modifications when plotting edges.
    :param counterclockwise_edge_kwargs: additional keyword arguments for plotting edges going counterclockwise. Default
        ``None`` makes no additional modifications when plotting edges.
    :param repeat_edge_kwargs: additional keyword arguments for plotting edges between repeat axes. Default ``None``
        makes no additional modifications when plotting edges.
    :param non_repeat_edge_kwargs: additional keyword arguments for plotting edges between non-repeat axes. Default
        ``None`` makes no additional modifications when plotting edges.
    :param warn_on_overlapping_kwargs: whether to warn if overlapping keyword arguments are detected among the
        ``"all_edge_kwargs"``, ``"repeat_edge_kwargs"``, ``"non_repeat_edge_kwargs"``, ``"clockwise_edge_kwargs"``, and
        ``"counterclockwise_edge_kwargs"`` parameters.
    :param num_steps_per_edge: how many steps to use in drawing each edge curve. Higher numbers will show smoother edges
        but take longer to compute and use more memory.
    :param collapsed_group_axis_name: name of the axis corresponding to the multiple partition groups collapsed onto a
        single axis. Only used when ``axes_order`` includes a ``None`` axis.
    :raises InvalidPartitionVariableError: if invalid ``partition_variable`` provided. This value must correspond to a
        column of the node data.
    :raises MissingSortingVariableError: if any of the axes resulting from the choice of ``partition_variable`` does not
        have a set sorting variable according to the ``sorting_variables`` parameter.
    :raises InvalidSortingVariableError: if the sorting variables chosen for one or more of the axes does not correspond
        to a column of the node data.
    :raises RepeatInPartitionAxisNameError: if one or more proposed axes set via the ``partition_variable`` ends in
        ``"_repeat"``, which is reserved for repeat axes.
    :raises InvalidAxisNameError: if provided ``axis_kwargs`` points to an axis not in the resulting ``HivePlot``
        instance.
    :raises InvalidAxesOrderError: if a non-``None`` ``axes_order`` includes any names that do not correspond to the
        partition set via the provided ``partition_variable``.
    :raises InvalidAxesOrderError: if user provides ``None`` as one of the axes in ``axes_order`` but there are no
        remaining unspecified names from the current partition to collapse onto this axis.
    """

    def __init__(
        self,
        nodes: NodeCollection,
        edges: Union[Edges, np.ndarray],
        partition_variable: Hashable,
        sorting_variables: Union[Hashable, Dict[Hashable, Hashable]],
        backend: SUPPORTED_VIZ_BACKENDS = "matplotlib",  # type: ignore
        repeat_axes: Union[bool, Hashable, List[Hashable]] = False,
        axes_order: Union[bool, List[Hashable]] = None,
        rotation: float = 0,
        angle_between_repeat_axes: float = 40,
        axis_kwargs: Optional[Dict[Hashable, Dict]] = None,
        all_edge_kwargs: Optional[dict] = None,
        clockwise_edge_kwargs: Optional[dict] = None,
        counterclockwise_edge_kwargs: Optional[dict] = None,
        repeat_edge_kwargs: Optional[dict] = None,
        non_repeat_edge_kwargs: Optional[dict] = None,
        warn_on_overlapping_kwargs: bool = True,
        num_steps_per_edge: int = 100,
        collapsed_group_axis_name: str = "Other",
    ) -> None:
        """
        Initialize class.
        """
        super().__init__()

        # track how many steps to use per hive plot edge
        self.num_steps_per_edge = num_steps_per_edge

        # track which viz backend we're using
        self.backend = None
        self.set_viz_backend(backend=backend)

        # hierarchy of edge kwargs, from least to most important
        #  latter edge kwargs will overwrite any overlapping settings in the former
        self._edge_kwarg_hierarchy = [
            "all_edge_kwargs",
            "clockwise_edge_kwargs",
            "counterclockwise_edge_kwargs",
            "repeat_edge_kwargs",
            "non_repeat_edge_kwargs",
        ]

        self.edge_plotting_keyword_arguments = {
            "all_edge_kwargs": {},
            "clockwise_edge_kwargs": {},
            "counterclockwise_edge_kwargs": {},
            "repeat_edge_kwargs": {},
            "non_repeat_edge_kwargs": {},
        }

        self.warn_on_overlapping_kwargs = warn_on_overlapping_kwargs

        self.add_nodes(nodes=nodes)
        self.add_edges(edges=edges)
        # which variable to use from node data to partition
        self.partition_variable = None
        # pandas groupy of partitioned node data
        self.partition = None
        # dictionary of sorting variable information
        #  with keys being unique partition values (axes names) and values being the sorting variable to use
        self.sorting_variables = {}
        # list of ordered axes for how they will be plotted
        self.axes_order = []
        # 1d numpy array of repeat axes
        self.repeat_axes = np.array([])
        # angle to use between repeat axes
        self.angle_between_repeat_axes = angle_between_repeat_axes
        # rotation of *all* axes relative to norm (equally spaced axes where first axis is placed at 0 degrees)
        self.rotation = rotation
        # name of collapsed group axis, if used
        self.collapsed_group_axis_name = collapsed_group_axis_name
        # set partition and partition_variable as well as repeat axes and sorting variables based on user input
        self.set_partition(
            partition_variable=partition_variable,
            sorting_variables=sorting_variables,
            repeat_axes=repeat_axes,
            axes_order=axes_order,
            collapsed_group_axis_name=collapsed_group_axis_name,
            build_hive_plot=False,
        )
        # build the hive plot axes based on all of these set inputs
        self.build_axes()

        # custom axes modifications after buildling the initial axes
        valid_keys = list(self.axes)
        if axis_kwargs is not None:
            for ax in axis_kwargs:
                if ax not in valid_keys:
                    raise InvalidAxisNameError(
                        f"{ax} not in partition variables {valid_keys}."
                    )
                self.update_axis(
                    axis_id=ax,
                    **axis_kwargs[ax],
                    build_hive_plot=False,
                )
                # repeat axis should default to same kwargs as non repeat axis if not specified by user
                repeat_axis_kwargs = {}
                if f"{ax}_repeat" in valid_keys:
                    # corner case, if a custom angle was specified for the non-repeat axis but not the repeat axis
                    #  then we need to redo the spacing with the repeat
                    #  (if the user specified the repeat angle too, then we leave the user's angle choice alone)
                    if "angle" in axis_kwargs[ax] and (
                        f"{ax}_repeat" not in axis_kwargs
                        or "angle" not in axis_kwargs[f"{ax}_repeat"]
                    ):
                        angle = self.axes[ax].angle - self.angle_between_repeat_axes / 2
                        repeat_angle = angle + self.angle_between_repeat_axes
                        self.update_axis(axis_id=ax, angle=angle, build_hive_plot=False)
                        repeat_axis_kwargs["angle"] = repeat_angle
                    # default same vmin / vmax span as non repeat axis if axes have same sorting variable
                    #   otherwise default span full extent of data
                    if (
                        self.sorting_variables[f"{ax}_repeat"]
                        == self.sorting_variables[ax]
                    ):
                        if not self.axes[ax].inferred_vmin and (
                            f"{ax}_repeat" not in axis_kwargs
                            or "vmin" not in axis_kwargs[f"{ax}_repeat"]
                        ):
                            repeat_axis_kwargs["vmin"] = self.axes[ax].vmin
                        else:
                            repeat_axis_kwargs["vmin"] = None
                        if not self.axes[ax].inferred_vmax and (
                            f"{ax}_repeat" not in axis_kwargs
                            or "vmax" not in axis_kwargs[f"{ax}_repeat"]
                        ):
                            repeat_axis_kwargs["vmax"] = self.axes[ax].vmax
                        else:
                            repeat_axis_kwargs["vmax"] = None
                    if (
                        f"{ax}_repeat" not in axis_kwargs
                        or "start" not in axis_kwargs[f"{ax}_repeat"]
                    ):
                        repeat_axis_kwargs["start"] = self.axes[ax].polar_start
                    if (
                        f"{ax}_repeat" not in axis_kwargs
                        or "end" not in axis_kwargs[f"{ax}_repeat"]
                    ):
                        repeat_axis_kwargs["end"] = self.axes[ax].polar_end
                    if "long_name" in axis_kwargs[ax] and (
                        f"{ax}_repeat" not in axis_kwargs
                        or "long_name" not in axis_kwargs[f"{ax}_repeat"]
                    ):
                        repeat_axis_kwargs["long_name"] = axis_kwargs[ax]["long_name"]

                    self.update_axis(
                        axis_id=f"{ax}_repeat",
                        **repeat_axis_kwargs,
                    )

        # rebuild axes with kwargs as needed and connect all the adjacent axes using any user-provided kwargs
        self.build_axes()

        all_edge_kwargs = all_edge_kwargs if all_edge_kwargs is not None else {}
        self.update_edge_plotting_keyword_arguments(
            edge_kwarg_setting="all_edge_kwargs",
            rebuild_edges=False,
            **all_edge_kwargs,
        )
        clockwise_edge_kwargs = (
            clockwise_edge_kwargs if clockwise_edge_kwargs is not None else {}
        )
        self.update_edge_plotting_keyword_arguments(
            edge_kwarg_setting="clockwise_edge_kwargs",
            rebuild_edges=False,
            **clockwise_edge_kwargs,
        )
        counterclockwise_edge_kwargs = (
            counterclockwise_edge_kwargs
            if counterclockwise_edge_kwargs is not None
            else {}
        )
        self.update_edge_plotting_keyword_arguments(
            edge_kwarg_setting="counterclockwise_edge_kwargs",
            rebuild_edges=False,
            **counterclockwise_edge_kwargs,
        )
        repeat_edge_kwargs = (
            repeat_edge_kwargs if repeat_edge_kwargs is not None else {}
        )
        self.update_edge_plotting_keyword_arguments(
            edge_kwarg_setting="repeat_edge_kwargs",
            rebuild_edges=False,
            **repeat_edge_kwargs,
        )
        non_repeat_edge_kwargs = (
            non_repeat_edge_kwargs if non_repeat_edge_kwargs is not None else {}
        )
        self.update_edge_plotting_keyword_arguments(
            edge_kwarg_setting="non_repeat_edge_kwargs",
            rebuild_edges=False,
            **non_repeat_edge_kwargs,
        )

        self.connect_adjacent_axes()

        # whether to warn user of the need to re-run the `build_hive_plot()` method before plotting.
        self.warn_on_plot = False

    @property
    def edge_kwarg_hierarchy(
        self,
    ) -> list:
        """
        Return the current ``edge_kwarg_hierarchy`` list, specified from least prioritized to most prioritized.
        """
        return self._edge_kwarg_hierarchy

    def _check_valid_axes(
        self,
        proposed_axes: Union[List[Hashable], np.ndarray],
        check_valid_with_partition: bool = True,
        check_repeat_in_name: bool = True,
    ) -> None:
        """
        Make sure proposed axes valid with current partition.

        Also check that proposed axes never end with ``"_repeat"``, as this is reserved for repeat axes.

        :param proposed_axes: proposed axes to use.
        :param check_valid_with_partition: whether to check if the ``proposed_axes`` are valid with current partition.
        :param check_repeat_in_name: whether to check if any of the ``proposed_axes`` end in ``"_repeat"``.
        :raises AssertionError: if one or more proposed axes are not in the current partition (if
            ``check_valid_with_partition=True``).
        :raises RepeatInPartitionAxisNameError: if one or more proposed axes ends in ``"_repeat"``, which is reserved
            for repeat axes (if ``check_repeat_in_name=True``).
        """
        if check_valid_with_partition:
            valid_axes = np.array([k for k, _ in self.partition])
            invalid_values = [a for a in proposed_axes if a not in valid_axes]
            assert len(invalid_values) == 0, (
                f"Proposed axes {list(proposed_axes)} has invalid values outside of current partition.\n"
                f"Specifically, proposed values {invalid_values} not contained in current partition values "
                f"{valid_axes}."
            )

        # make sure users don't make variables that end in "_repeat" since that is a protected phrase.
        if check_repeat_in_name and any(
            i[-7:] == "_repeat" for i in proposed_axes if isinstance(i, str)
        ):
            raise RepeatInPartitionAxisNameError(
                "Proposed axes names must never end with '_repeat', as this naming is reserved for repeat axes. "
                f"Current names being generated parititioning with variable {self.partition_variable}: {proposed_axes}."
            )

    def set_repeat_axes(
        self,
        axes_names: Union[bool, Hashable, List[Hashable]],
        sorting_variables: Optional[Union[Hashable, Dict[Hashable, Hashable]]] = None,
        build_hive_plot: bool = True,
        preserve_original_edge_kwargs: bool = True,
    ) -> None:
        """
        Set repeat axes for specified axes names.

        .. note::
            This method will *overwrite* existing repeat axes specifications. Thus, rerunning this method will remove
            any repeat axes not specified in the call. See the example code below.

            If a necessary repeat axis sorting variable is not provided by the user, then this method will use the
            sorting variable from the corresponding non-repeat axis.

            Any existing repeat axes can be removed by setting ``axes_names`` to ``False`` or ``[]``.

        .. code-block:: python

            from hiveplotlib.datasets import example_hive_plot

            hp = example_hive_plot()
            list(hp.axes.keys())
            >>> ['A', 'B', 'C']

            # adds 'A_repeat'
            hp.set_repeat_axes("A")
            list(hp.axes.keys())
            >>> ['A', 'B', 'C', 'A_repeat']

            # removes 'A_repeat', adds 'B_repeat'
            hp.set_repeat_axes("B")
            list(hp.axes.keys())
            >>> ['B', 'C', 'A', 'B_repeat']

        :param axes_names: axes names for which to create repeat axes. Providing ``True`` here turns on all
            possible axes specified via the ``partition`` attribute. ``False`` or ``[]`` turns off all repeat axes.
        :param sorting_variables: sorting variables to choose for the axis / axes.
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :raises AssertionError: if one or more proposed axes are not in the current partition.
        :raises RepeatInPartitionAxisNameError: if one or more proposed axes for which to add a repeat ends in
            ``"_repeat"``.
        :return: ``None``.
        """
        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        original_repeat_axes = self.repeat_axes.copy()
        if axes_names is True:
            self.repeat_axes = np.array([k for k, _ in self.partition])
        elif axes_names is False:
            self.repeat_axes = np.array([])
        # otherwise, double check we have valid values
        elif axes_names is not False:
            proposed_repeat_axes = np.array(
                axes_names
            ).flatten()  # make sure hashable input becomes iterable
            # make sure proposed repeat axes are valid
            self._check_valid_axes(proposed_axes=proposed_repeat_axes)
            self.repeat_axes = proposed_repeat_axes

        removed_repeat_axes = set(original_repeat_axes.tolist()).difference(
            set(self.repeat_axes.tolist())
        )
        for ax in removed_repeat_axes:
            repeat_axis_name = f"{ax}_repeat"

            # remove the dropped repeat axis and any edges connecting to and from it
            self.reset_edges(axis_id_1=repeat_axis_name)
            del self.axes[repeat_axis_name]

            # switch the angle of the non-repeat axis back to the non-repeat angle
            original_angle = self.axes[ax].angle
            new_angle = original_angle + self.angle_between_repeat_axes / 2
            self.update_axis(
                axis_id=ax,
                angle=new_angle,
                build_hive_plot=False,
            )

        # update sorting variables for any newly-added axes
        repeat_axis_names = [f"{ax}_repeat" for ax in self.repeat_axes]
        if sorting_variables is not None and isinstance(sorting_variables, Hashable):
            sorting_variables_dict = dict.fromkeys(repeat_axis_names, sorting_variables)

        elif isinstance(sorting_variables, dict) or sorting_variables is None:
            if sorting_variables is None:
                sorting_variables = {}
            # if sorting variables are specified, use them
            # otherwise, use the existing sorting variables
            sorting_variables_dict = {}
            for ax in self.repeat_axes:
                repeat_axis_name = f"{ax}_repeat"
                # if sorting variable for repeat axis is specified, use it
                if repeat_axis_name in sorting_variables:
                    sorting_variables_dict[repeat_axis_name] = sorting_variables[
                        repeat_axis_name
                    ]
                # we will accept user specifying name without "_repeat" here too
                elif ax in sorting_variables:
                    sorting_variables_dict[repeat_axis_name] = sorting_variables[ax]
                # fall back to the existing repeat axis sorting variable
                elif repeat_axis_name in self.sorting_variables:
                    sorting_variables_dict[repeat_axis_name] = self.sorting_variables[
                        repeat_axis_name
                    ]
                # lastly, fall back to the existing non-repeat axis sorting variable
                elif ax in self.sorting_variables:
                    sorting_variables_dict[repeat_axis_name] = self.sorting_variables[
                        ax
                    ]
                else:  # pragma: no cover
                    # if no sorting variable is specified, raise an error
                    # but this should be impossible to get to in the code
                    raise MissingSortingVariableError(
                        f"Repeat axis {repeat_axis_name} has no sorting variable specified.\n"
                        f"This should be impossible to hit! We'd appreciate if you could file a bug report here:\n"
                        "https://gitlab.com/geomdata/hiveplotlib/-/issues/new"
                    )
        else:  # pragma: no cover
            raise NotImplementedError(
                "Unsupported format for `sorting_variables` parameter."
            )
        self.update_sorting_variables(
            sorting_variables=sorting_variables_dict,
            build_hive_plot=False,
        )

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        if build_hive_plot:
            self.build_hive_plot(
                preserve_original_edge_kwargs=preserve_original_edge_kwargs
            )
        else:
            self.warn_on_plot = True

        return

    def update_sorting_variables(
        self,
        sorting_variables: Union[Hashable, Dict[Hashable, Hashable]],
        reset_vmin_and_vmax: bool = True,
        build_hive_plot: bool = True,
        preserve_original_edge_kwargs: bool = True,
    ) -> None:
        """
        Update sorting variables for specified axes with the current partition.

        :param sorting_variables: sorting variable(s) to use for axes. Can specify a single value to use for all axes or
            a dictionary with axis name keys and sorting variable values to assign specific sorting variables to
            individual axes. Unless overwriting all current sorting variables, previously set sorting variables will be
            preserved.
        :param reset_vmin_and_vmax: if True, then setting a sorting variable for an axis / axes will throw out any
            existing ``vmin`` / ``vmax`` information, reinitializing to infer and span the full extent of data (i.e.
            ``vmin=None`` and ``vmax=None``).
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :raises MissingSortingVariableError: if not all of the current partition axes have been specified with a sorting
            variable (either from the current call or from earlier, either with another call to this method or by
            setting ``sorting_variables`` on initialization of the ``HivePlot`` instance.
        :raises InvalidSortingVariableError: if the sorting variables chosen for one or more of the axes does not
            correspond to a column of the node data.
        :return: ``None``.

        .. note::
            If specifying a dictionary of ``sorting_variables`` information, any axes keys excluded from the provided
            dictionary will be unaffected, each keeping its existing sorting variable.

            Repeat axes can be specified by specifying the repeat axis name, which will be
            ``"<partition_value>_repeat"`` for whatever ``<partition_value>`` to which an axis corresponds.

            Providing an *invalid* sorting variable value will raise a ``InvalidSortingVariableError``.

            A ``Hashable`` input will set the sorting variable of all *possible* axes with the current ``partition``
            attribute, including all possible repeat axes (whether plotted or not), to use the provided sorting
            variable. Any sorting variables set for a previous partition axis will be preserved.

            If ``reset_vmin_and_vmax=True``, then setting a sorting variable for an axis will throw out any existing
            ``vmin`` / ``vmax`` information for the provided axis / axes, reinitializing to infer and span the full
            extent of data (i.e. ``vmin=None`` and ``vmax=None``).

            Providing a nonexistent axis key will not raise any error. Instead, the sorting variable for the nonexistent
            axis will be stored in the ``sorting_variables`` attribute dictionary, leaving current axes unaffected. This
            allows users to set sorting variables for multiple partitions at once without setting the sorting variables
            everytime the partition variable is changed.
        """
        if not isinstance(sorting_variables, dict):
            # if specifying same sorting variable for all axes, also propagate to the collapsed group axis name
            axes_to_update = list(self.axes.keys()) + [self.collapsed_group_axis_name]
            original_sorting_variable = sorting_variables
            sorting_variables = {
                k: original_sorting_variable for k, _ in self.partition
            }
            # also add in all possible repeat axes labels for current partition
            for k, _ in self.partition:
                sorting_variables[f"{k}_repeat"] = original_sorting_variable

        else:
            axes_to_update = list(sorting_variables.keys())

        # make sure all the sorting variables are valid before assigning new `sorting_variables` attribute
        for k in sorting_variables:
            if sorting_variables[k] not in self.nodes.data.columns:
                raise InvalidSortingVariableError(
                    f"Invalid `sorting_variables` ('{sorting_variables[k]}') provided for axis {k}, "
                    f"must be column of node data: {self.nodes.data.columns.to_list()}"
                )

        # otherwise, double check we have valid axis values
        proposed_axes = list(sorting_variables.keys())

        # update existing dict with any new provided variables
        self.sorting_variables.update(sorting_variables)

        # sorting variables must cover all axes dictated by `self.partition` plus any repeat axes
        expected_axes_names = set(
            [k for k, _ in self.partition]
            + [f"{repeat_axis}_repeat" for repeat_axis in self.repeat_axes]
        )
        missing_axes = expected_axes_names.difference(
            set(self.sorting_variables.keys())
        )
        if len(missing_axes) > 0:
            raise MissingSortingVariableError(
                f"Provided `sorting_variables` axes {list(proposed_axes)} do not cover *all* the necessary axes "
                f"specified by the current partition: ({list(expected_axes_names)}).\n"
                f"The following axes specifications must be included: {list(missing_axes)}"
            )

        update_axis_kwargs = {}
        if reset_vmin_and_vmax:
            update_axis_kwargs["vmin"] = None
            update_axis_kwargs["vmax"] = None

        # update axes if they exist
        for axis in axes_to_update:
            if axis in self.axes:
                self.update_axis(
                    axis_id=axis,
                    sorting_variable=sorting_variables[axis],
                    **update_axis_kwargs,
                    preserve_original_edge_kwargs=preserve_original_edge_kwargs,
                    build_hive_plot=False,  # building it below, this is redundant
                )

        if build_hive_plot:
            self.build_hive_plot(
                preserve_original_edge_kwargs=preserve_original_edge_kwargs,
            )
        else:
            self.warn_on_plot = True

        return

    def _set_partition(self, partition_variable: Hashable) -> None:
        """
        Set the node partition variable only, dropping now-invalid content from class attributes.

        :param partition_variable: node partition variable to use.
        :raises InvalidPartitionVariableError: if invalid ``partition_variable`` provided.
        :return: ``None``.
        """
        if partition_variable not in self.nodes.data.columns:
            raise InvalidPartitionVariableError(
                f"Invalid `partition_variable` ('{partition_variable}') provided, "
                f"must be column of node data: {self.nodes.data.columns.to_list()}"
            )

        partition = self.nodes.data.groupby(partition_variable)

        # confirm partition creates valid axis names
        self._check_valid_axes(
            proposed_axes=[i for i, _ in partition],
            check_valid_with_partition=False,  # haven't set the partition yet
        )

        # drop all existing edges and axes (old edges and axes are irrelevant with new partition)
        self.reset_edges()
        self.axes = {}
        self.repeat_axes = np.array([])

        self.partition_variable = partition_variable
        self.partition = partition

        return

    def set_partition(
        self,
        partition_variable: Hashable,
        sorting_variables: Union[Hashable, Dict[Hashable, Hashable]],
        repeat_axes: Union[bool, Hashable, List[Hashable]] = False,
        axes_order: Optional[Union[List[Hashable], np.ndarray]] = None,
        collapsed_group_axis_name: str = "Other",
        build_hive_plot: bool = True,
    ) -> None:
        """
        Set the node partition variable, create the necessary axes, and place nodes on the axes accordingly.

        .. note::
            This call will remove any existing axes.

        :param partition_variable: node partition variable to use.
        :param sorting_variables: sorting variable(s) to use for axes. Can specify a single value to use for all axes or
            a dictionary with axis name keys and sorting variable values to assign specific sorting variables to
            individual axes. Repeat axes can be specified by specifying the resulting axis name, which will be
            ``"<partition_value>_repeat"`` for whatever ``<partition_value>`` to which an axis corresponds.
        :param repeat_axes: axes names for which to create repeat axes. Providing ``True`` here turns on all
            possible axes specified via the ``partition`` attribute. ``False`` or ``[]`` turns off all repeat axes.
        :param axes_order: unique names available in the column of data corresponding to the ``partition_variable``
            attribute. Names must correspond to the unique values in node data specified by the current
            ``partition_variable``. If a list of ``axes_order`` names are provided *and* one of the names in the
            provided list is ``None``, then all remaining values unspecified in the provided list that are in the
            current partition as specified by ``partition_variable`` will be collapsed onto a single axis. This is
            particularly useful when the partition variable has more than 3 values. To change the name of the collapsed
            group in the final hive plot visualization, see the ``collapsed_group_axis_name`` parameter. Default
            ``None`` uses the order in the ``pandas`` groupby object stored in the resulting ``partition`` attribute.
        :param collapsed_group_axis_name: name of the axis corresponding to the multiple partition groups collapsed onto
            a single axis. Only used when ``axes_order`` includes a ``None`` axis.
        :param build_hive_plot: whether to rebuild the hive plot (i.e. recompute axes and redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :return: ``None``.
        :raises InvalidPartitionVariableError: if invalid ``partition_variable`` provided.
        :raises RepeatInPartitionAxisNameError: if one or more implied axes names from the given partition would end in
            ``"_repeat"``. This naming convention is reserved for repeat axes.
        :raises InvalidAxesOrderError: if non-``None`` ``axes_order`` parameter provides names outside of the current
            partition.
        :raises InvalidAxesOrderError: if user provides ``None`` as one of the axes but there are no remaining
            unspecified names from the current partition to collapse onto this axis.
        """
        self._set_partition(partition_variable=partition_variable)

        self.set_axes_order(
            axes=axes_order,
            collapsed_group_axis_name=collapsed_group_axis_name,
            build_hive_plot=False,
            check_collapsed_group_sorting_variable=False,  # gets checked below
            require_using_all_partition_names=False,  # not necessary when rebuilding all axes
        )

        self.update_sorting_variables(
            sorting_variables=sorting_variables,
            build_hive_plot=False,
        )

        self.set_repeat_axes(
            axes_names=repeat_axes,
            sorting_variables=sorting_variables,
            build_hive_plot=False,
        )

        if build_hive_plot:
            self.build_hive_plot(
                build_axes_from_scratch=True,
            )
        else:
            self.warn_on_plot = True

        return

    def update_partition_data(self) -> None:
        """
        Update the partition data based on the current node data.

        This method is useful when the node data has changed, which means the partition needs to be recalculated and
        the resulting new data propagating to the axes.

        this method will reset the partition and update the axes accordingly.

        :return: ``None``.
        """
        axes_order = [
            i if i != self.collapsed_group_axis_name else None for i in self.axes_order
        ]
        self.set_partition(
            partition_variable=self.partition_variable,
            sorting_variables=self.sorting_variables,
            repeat_axes=self.repeat_axes,
            axes_order=axes_order,
            collapsed_group_axis_name=self.collapsed_group_axis_name,
        )

        return

    def set_axes_order(
        self,
        axes: Optional[Union[List[Union[Hashable, None]], np.ndarray]] = None,
        collapsed_group_axis_name: Optional[str] = None,
        collapsed_group_sorting_variable: Optional[Hashable] = None,
        build_hive_plot: bool = True,
        preserve_original_edge_kwargs: bool = True,
        check_collapsed_group_sorting_variable: bool = True,
        require_using_all_partition_names: bool = True,
    ) -> None:
        """
        Set order of axes to be plotted in counterclockwise order.

        Names must correspond to the unique values in node data specified by the ``partition_variable`` attribute, or
        users can provide ``None`` as one of the axes to collapse any unspecified groups from the partition onto a
        single axis.

        Default ``None`` uses the order in the ``pandas`` groupby object stored in the ``partition`` attribute.

        .. note::
            If a user is trying to set a subset of the partition names under the ``axes`` parameter (without a ``None``
            collapsing axis), then the user should instead call ``set_partition()`` with the desired ``axes_order``
            subset of names.

        :param axes: unique names available in the column of data corresponding to the ``partition_variable`` attribute.
            Names must correspond to the unique values in node data specified by the current ``partition_variable``. If
            a list of ``axes`` names are provided *and* one of the names in the provided list is ``None``, then all
            remaining values unspecified in the provided list that are in the current partition as specified by
            ``partition_variable`` will be collapsed onto a single axis. This is particularly useful when the partition
            variable has more than 3 values. To change the name of the collapsed group in the final hive plot
            visualization, see the ``collapsed_group_axis_name`` parameter. Default ``None`` uses the order in the
            ``pandas`` groupby object stored in the resulting ``partition`` attribute.
        :param collapsed_group_axis_name: name of the axis corresponding to the multiple partition groups collapsed onto
            a single axis. Only used when ``axes_order`` includes a ``None`` axis. Default ``None`` uses the name
            stored under the ``collapsed_group_axis_name`` attribute.
        :param collapsed_group_sorting_variable: sorting variable to use for the collapsed group axis. If not provided,
            and a value is not available in the ``sorting_variables`` attribute, then a ``MissingSortingVariableError``
            will be raised.
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :param check_collapsed_group_sorting_variable: whether to check if a collapsed group sorting variable exists.
        :param require_using_all_partition_names: whether to require that the user provides all partition names in the
            ``axes`` parameter. If ``True``, then the user must provide all partition names, or at least provide
            ``None`` to collapse any unspecified groups onto a single axis. If trying to set a subset of the
            partition names, then the user should instead call ``set_partition()`` with the desired ``axes_order``.
        :return: ``None``.
        :raises InvalidAxesOrderError: if non-``None`` ``axes`` parameter provides names outside of the current
            partition.
        :raises InvalidAxesOrderError: if user provides a strict subset of partition axes values and
            ``require_using_all_partition_names=True``.
        :raises InvalidAxesOrderError: if user provides ``None`` as one of the axes but there are no remaining
            unspecified names from the current partition to collapse onto this axis.
        :raises MissingSortingVariableError: if the sorting variable for the collapsed group axis is not provided and a
            value is not available for the collapsed group axis under the ``sorting_variables`` attribute. Note, check
            only runs if ``check_collapsed_group_sorting_variable`` is True.
        """
        # when realigning the axes, always work off of the TRUE partition, never the collapsed one
        if "_collapsed_axis" in self.partition_variable:
            self._set_partition(
                partition_variable=self.partition_variable.removesuffix(
                    "_collapsed_axis"
                )
            )

        valid_names = [k for k, _ in self.partition]

        if axes is None:
            self.axes_order = valid_names
            return

        provided_axes_not_in_partition = set(axes).difference(set(valid_names))

        # either all provided axes names are in partition, or the only one not in the partition is the variable `None`
        unacceptable_names = (
            provided_axes_not_in_partition != set()
            and provided_axes_not_in_partition != {None}
        )

        if unacceptable_names:
            raise InvalidAxesOrderError(
                "Axes order set with incorrect names "
                f"for the current partition variable {self.partition_variable}.\n"
                f"Axes names that must be provided (in any order): {list(valid_names)}.\n"
                "(Can also include `None` to collapse any unspecifed groups from the partition into a single axis.)\n"
                f"Names provided: {list(axes)}."
            )

        if None in axes:
            unspecified_axes = set(valid_names).difference(set(axes))
            if len(unspecified_axes) == 0:
                raise InvalidAxesOrderError(
                    "Provided `None` in for axes order, but no unspecified axes to collapse onto this 'Other' axis.\n"
                    f"Axes order names provided: {list(axes)}."
                )

            if collapsed_group_axis_name is not None:
                self.collapsed_group_axis_name = collapsed_group_axis_name

            # update partition to play nice if `None` axis provided
            current_partition_values = self.nodes.data[
                self.partition_variable
            ].to_numpy()

            unique_strings = np.unique(current_partition_values)

            indices = np.searchsorted(unique_strings, current_partition_values)

            replacement_map = dict.fromkeys(
                unspecified_axes, self.collapsed_group_axis_name
            )

            replacement_strings = np.array(
                [replacement_map.get(s, s) for s in unique_strings]
            )
            collapsed_partition_values = replacement_strings[indices]

            new_partition_variable_name = self.partition_variable + "_collapsed_axis"

            self.nodes.data[new_partition_variable_name] = collapsed_partition_values

            if collapsed_group_sorting_variable is not None:
                self.sorting_variables[self.collapsed_group_axis_name] = (
                    collapsed_group_sorting_variable
                )
            if (
                check_collapsed_group_sorting_variable
                and self.collapsed_group_axis_name not in self.sorting_variables
            ):
                raise MissingSortingVariableError(
                    f"Sorting variable for collapsed group axis {self.collapsed_group_axis_name} not provided and "
                    f"not available in the current sorting variables: {self.sorting_variables}"
                )

            # use new name for axes downstream
            axes = [
                i if i is not None else self.collapsed_group_axis_name for i in axes
            ]
            self._set_partition(partition_variable=new_partition_variable_name)

        elif require_using_all_partition_names:
            # if we are requiring all partition names, then make sure we have all of them
            missing_partition_names = set(valid_names).difference(set(axes))
            if len(missing_partition_names) > 0:
                raise InvalidAxesOrderError(
                    f"Provided axes order {list(axes)} does not include all partition names: {list(valid_names)}.\n"
                    f"Missing partition names: {list(missing_partition_names)}.\n"
                    "If you want to only show a subset of the partition names, then run set_partition() with the "
                    "desired `axes_order`."
                )

        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        # drop all existing edges and change all axes angles (old edges and axes are irrelevant with axes moving around)
        self.reset_edges()

        # space out axes evenly
        spacing = 360 / len(self.partition)

        # update any existing axes angles
        #  (nonexistent axes will be plotted correctly if plotted for the first time later)
        for i, axis in enumerate(axes):
            angle = spacing * i + self.rotation
            if axis in self.repeat_axes:
                # update angle accordingly for both axis and repeat axis
                angle -= self.angle_between_repeat_axes / 2
                repeat_angle = angle + self.angle_between_repeat_axes
                if f"{axis}_repeat" in self.axes:
                    self.update_axis(
                        axis_id=f"{axis}_repeat",
                        angle=repeat_angle,
                        build_hive_plot=False,
                    )
            if axis in self.axes:
                self.update_axis(
                    axis_id=axis,
                    angle=angle,
                    build_hive_plot=False,
                )
        self.axes_order = list(axes)

        # reorder self.partition based on axes order
        groupby_dict = {i: j for (i, j) in self.partition}  # noqa: C416
        self.partition = [(i, groupby_dict[i]) for i in self.axes_order]

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        if build_hive_plot:
            self.build_hive_plot(
                preserve_original_edge_kwargs=preserve_original_edge_kwargs,
            )
        else:
            self.warn_on_plot = True

        return

    def set_rotation(
        self,
        rotation: float,
        build_hive_plot: bool = True,
        preserve_original_edge_kwargs: bool = True,
    ) -> None:
        """
        Rotate all axes counterclockwise relative to the default placement, then reconstruct axes and edges accordingly.

        By default, axes are equally spaced in polar coordinates, with the first axis placed at an angle of 0 degrees.

        Changing the rotation angle will rotate *every* axis counterclockwise by the provided ``rotation`` value
        (measured in degrees).

        :param rotation: angle (measured in degrees) to rotate *every* axis counterclockwise off of the default value.
            (By default, axes are evenly spaced in polar coordinates, with the first axis drawn at an angle of 0
            degrees.)
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :return: ``None``.
        """
        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        # drop all existing edges which will need to be redrawn since axes are moving
        self.reset_edges()
        original_rotation = self.rotation

        axes_to_rotate = self.axes.copy().keys()
        for axis in axes_to_rotate:
            current_angle = self.axes[axis].angle
            # subtract out initial rotation and add in new rotation
            revised_rotation_angle = current_angle - original_rotation + rotation
            self.update_axis(
                axis_id=axis,
                angle=revised_rotation_angle,
                build_hive_plot=False,
            )

        self.rotation = rotation

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        if build_hive_plot:
            self.build_hive_plot(
                preserve_original_edge_kwargs=preserve_original_edge_kwargs,
            )
        else:
            self.warn_on_plot = True

        return

    def set_angle_between_repeat_axes(
        self,
        angle: float = 40,
        build_hive_plot: bool = True,
        preserve_original_edge_kwargs: bool = True,
    ) -> None:
        """
        Set the angle (in degrees) between repeat axes.

        :param angle: angle (in degrees) to use between repeat axes.
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :return: ``None``.
        """
        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        # drop all existing edges which will need to be redrawn since axes are moving
        self.reset_edges()

        original_angle_between_repeat_axes = self.angle_between_repeat_axes

        # need to reset angle of any *existing* axes and / or their repeats
        for axis in self.repeat_axes:
            # unless we are dealing with custom placement of the repeat axis, in which case we will leave the pair alone
            expected_repeat_axis_placement = (
                self.axes[axis].angle + original_angle_between_repeat_axes
            ) % 360
            if expected_repeat_axis_placement != self.axes[f"{axis}_repeat"].angle:
                continue

            # revise base axis corresponding to current repeat axis if already exists
            #  (if doesn't exist, it will be generated correctly on `self.build_hive_plot()`)
            if axis in self.axes:
                current_angle = self.axes[axis].angle
                # shift back to non-repeat angle, then shift by new angle
                new_angle = (
                    current_angle + original_angle_between_repeat_axes / 2 - angle / 2
                )
                self.update_axis(
                    axis_id=axis,
                    angle=new_angle,
                    build_hive_plot=False,
                )

            # revise repeat axis if already exists
            #  (if doesn't exist, it will be generated correctly on `self.build_hive_plot()`)
            repeat_axis = f"{axis}_repeat"
            if repeat_axis in self.axes:
                current_angle = self.axes[repeat_axis].angle
                # shift back to non-repeat angle, then shift by new angle
                new_angle = (
                    current_angle - original_angle_between_repeat_axes / 2 + angle / 2
                )
                self.update_axis(
                    axis_id=repeat_axis,
                    angle=new_angle,
                    build_hive_plot=False,
                )

        self.angle_between_repeat_axes = angle

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        if build_hive_plot:
            self.build_hive_plot(
                preserve_original_edge_kwargs=preserve_original_edge_kwargs
            )
        else:
            self.warn_on_plot = True

        return

    def set_viz_backend(self, backend: SUPPORTED_VIZ_BACKENDS) -> None:  # type: ignore
        """
        Set viz backend for plotting.

        :param backend: which viz backend to use for plotting.
        :raises AssertionError: if user tries to set an unsupported viz backend.
        :return: ``None``.
        """
        if backend not in get_args(SUPPORTED_VIZ_BACKENDS):
            raise InvalidVizBackendError(
                f"Requested backend '{backend}' not among supported backends {get_args(SUPPORTED_VIZ_BACKENDS)}."
            )
        self.backend = backend

        return

    def __populate_original_edge_kwargs(self, original_edge_info: dict) -> None:
        """
        Populate edge kwargs from ``original_edge_info`` into the ``hive_plot_edges`` attribute.

        ``original_edge_info`` is intended to be a copy of the ``hive_plot_edges`` attribute.

        :param original_edge_info: edge information from which to populate the ``hive_plot_edges`` attribute
            (``edge_kwargs`` values only).
        """
        for a0 in original_edge_info:
            for a1 in original_edge_info[a0]:
                for tag in original_edge_info[a0][a1]:
                    if "edge_kwargs" in original_edge_info[a0][a1][tag]:
                        if a0 not in self.hive_plot_edges:
                            self.hive_plot_edges[a0] = {}
                        if a1 not in self.hive_plot_edges[a0]:
                            self.hive_plot_edges[a0][a1] = {}
                        if tag not in self.hive_plot_edges[a0][a1]:
                            self.hive_plot_edges[a0][a1][tag] = {}
                        self.hive_plot_edges[a0][a1][tag]["edge_kwargs"] = (
                            original_edge_info[a0][a1][tag]["edge_kwargs"]
                        )
        return

    def update_edges(
        self,
        partition_id_1: Hashable,
        partition_id_2: Hashable,
        tag: Optional[Hashable] = None,
        p1_to_p2: bool = True,
        p2_to_p1: bool = True,
        short_arc: Optional[bool] = None,
        control_rho_scale: Optional[float] = None,
        control_angle_shift: Optional[float] = None,
        reset_existing_kwargs: bool = False,
        overwrite_existing_kwargs: bool = True,
        **edge_kwargs,
    ) -> None:
        """
        Modify all existing edges between a pair of partition groups.

        This method allows changing edge construction parameters and / or edge visualization keyword arguments.

        .. note::
            This method also allows for modification of edges in just one direction between the two provided partition
            groups by specifying `p1_to_p2` or `p2_to_p1` as False (both are True by default).

            Any updates done via this method will be lost if one calls the
            :py:meth:`hiveplotlib.HivePlot.build_hive_plot()` method.

        :param partition_id_1: Hashable pointer to the first group in the current partition between which we
            want to modify connections.
        :param axis_id_2: Hashable pointer to the second group in the current partition between which we
            want to modify connections.
        :param tag: unique ID specifying which tag of edges to modify.
            Note, if no tag is specified (e.g. ``tag=None``), it is presumed there is only one tag for the specified
            set of partition IDs to look over, which can be inferred. If no tag is specified and there are multiple tags
            to choose from, an ``UnspecifiedTagError`` will be raised.
        :param p1_to_p2: whether to modify connections going FROM ``partition_id_1`` TO ``partition_id_2``.
        :param p2_to_p1: whether to modify connections going FROM ``partition_id_2`` TO ``partition_id_1``.
        :param short_arc: whether to take the shorter angle arc (``True``) or longer angle arc (``False``).
            When not set, uses a default value ``True``.
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default ``True``.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (``short_arc=False``). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :param control_rho_scale: how much to multiply the distance of the control point for each edge to / from the
            origin. When not set, uses a default value ``1``, which sets the control rho for each edge as the mean rho
            value for each pair of nodes being connected by that edge. A value greater than 1 will pull the resulting
            edges further away from the origin, making edges more convex, while a value between 0 and 1 will pull the
            resulting edges closer to the origin, making edges more concave. Note, this affects edges further from the
            origin by larger magnitudes than edges closer to the origin.
        :param control_angle_shift: how far to rotate the control point for each edge around the origin. When not set,
            uses a default value ``0``, which sets the control angle for each edge as the mean polar angle for each pair
            of nodes being connected by that edge. A positive value will pull the resulting edges further
            counterclockwise, while a negative value will pull the resulting edges further clockwise.
        :param reset_existing_kwargs: whether to delete existing edge kwargs stored in
            the ``hive_plot_edges`` attribute for the specified edges, default leaves the existing edge kwargs
            unchanged, overwriting any provided kwargs accordingly.
        :param overwrite_existing_kwargs: whether to overwrite existing edge kwargs stored in
            the ``hive_plot_edges`` attribute for the specified edges when also provided in ``edge_kwargs``, default
            True.
        :param edge_kwargs: additional params that will be applied to the related edges.
        :return: ``None``.
        :raises InvalidPartitionVariableError: if invalid partition variables provided with respect to the current
            partition.
        :raises UnspecifiedTagError: if no tag is specified and there are multiple tags available.
        """
        valid_partition_variables = [i for i, _ in self.partition]
        if (
            partition_id_1 not in valid_partition_variables
            or partition_id_2 not in valid_partition_variables
        ):
            raise InvalidPartitionVariableError(
                "Invalid partition variables (`partition_id_1` or `partition_id_2`) provided. "
                f"Must be one of: {valid_partition_variables}."
            )

        # default params will come from original settings
        edges_instantiation_params = {
            "short_arc": True,
            "control_rho_scale": 1,
            "control_angle_shift": 0,
        }

        directions_to_check = []
        if p1_to_p2:
            directions_to_check.append([partition_id_1, partition_id_2])
        if p2_to_p1:
            directions_to_check.append([partition_id_2, partition_id_1])
        any_found_edges = False  # if we ever find edges to modify
        for repeat_suffix_1, repeat_suffix_2 in [
            ["", ""],  # non-repeat to non-repeat
            ["_repeat", ""],  # repeat to non-repeat
            ["", "_repeat"],  # non-repeat to repeat
        ]:
            for partition_1, partition_2 in directions_to_check:
                found_edges = False
                # find which axes between two groups are *actually* connected with edges (i.e. have edge curves)
                p1 = f"{partition_1}{repeat_suffix_1}"
                p2 = f"{partition_2}{repeat_suffix_2}"
                if (
                    p1 in self.hive_plot_edges
                    and p2 in self.hive_plot_edges[p1]
                    and len(self.hive_plot_edges[p1][p2]) > 0
                ):
                    if len(self.hive_plot_edges[p1][p2]) > 1 and tag is None:
                        raise UnspecifiedTagError(
                            "`tag` must be specified when there are multiple tags."
                        )
                    if tag is None:
                        tag = list(self.hive_plot_edges[p1][p2].keys())[0]
                    if (
                        tag in self.hive_plot_edges[p1][p2]
                        and "curves" in self.hive_plot_edges[p1][p2][tag]
                        and len(self.hive_plot_edges[p1][p2][tag]["curves"]) > 0
                    ):
                        axis_id_1 = p1
                        axis_id_2 = p2
                        found_edges = True
                        any_found_edges = True

                    # don't bother rebuilding edges unless at least one relevant parameter is changed
                    if found_edges and any(
                        i is not None
                        for i in [short_arc, control_rho_scale, control_angle_shift]
                    ):
                        if short_arc is not None:
                            edges_instantiation_params["short_arc"] = short_arc
                        if control_rho_scale is not None:
                            edges_instantiation_params["control_rho_scale"] = (
                                control_rho_scale
                            )
                        if control_angle_shift is not None:
                            edges_instantiation_params["control_angle_shift"] = (
                                control_angle_shift
                            )

                        del self.hive_plot_edges[axis_id_1][axis_id_2][tag]["curves"]
                        self.add_edge_curves_between_axes(
                            axis_id_1=axis_id_1,
                            axis_id_2=axis_id_2,
                            tag=tag,
                            a1_to_a2=True,
                            a2_to_a1=False,
                            num_steps=self.num_steps_per_edge,
                            **edges_instantiation_params,
                        )

                    if found_edges:
                        self.add_edge_kwargs(
                            axis_id_1=axis_id_1,
                            axis_id_2=axis_id_2,
                            tag=tag,
                            a1_to_a2=True,
                            a2_to_a1=False,
                            overwrite_existing_kwargs=overwrite_existing_kwargs,
                            reset_existing_kwargs=reset_existing_kwargs,
                            warn_on_no_edges=True,
                            **edge_kwargs,
                        )

        if not any_found_edges:
            warnings.warn(
                "Found no edges to modify between specified partion groups in the requested directions:"
                f"'{partition_id_1}' and '{partition_id_2}'.\n"
                "No changes made from this `update_edges()` call.",
                stacklevel=2,
            )

        return

    def update_axis(
        self,
        axis_id: Hashable,
        sorting_variable: Optional[Hashable] = None,
        vmin: Union[float, None, Literal["unchanged"]] = "unchanged",
        vmax: Union[float, None, Literal["unchanged"]] = "unchanged",
        start: Optional[float] = None,
        end: Optional[float] = None,
        angle: Optional[float] = None,
        long_name: Optional[Hashable] = None,
        preserve_original_edge_kwargs: bool = True,
        build_hive_plot: bool = True,
    ) -> None:
        """
        Update existing axis parameters.

        Allows updating axis size, axis placement in cartesian space, the long name for axis labeling during plotting,
        node sorting, and positioning nodes on the axis.

        When running on a given axis, any unspecified parameters will remain unchanged from the axis' original values.

        .. note::
            If a ``sorting_variable`` parameter is provided, and the axis was previously inferring the vmin / vmax,
            then the default behavior of the ``vmin`` / ``vmax`` parameter, if not provided, will be to
            re-determine the global minimum / maximum for the new feature values (i.e. as if the parameter were set to
            ``None``).

        :param axis_id: unique name for ``Axis`` instance.
        :param sorting_variable: node sorting variable to use. Default ``None`` maintains existing sorting variable.
            If the ``vmin`` and / or ``vmax`` value was previously inferred, then it will be re-inferred according to
            the global min and / or max values of this new sorting variable.
        :param vmin: all values less than ``vmin`` will be set to ``vmin``. ``None`` infers and sets as global minimum
            of feature values for all ``Node`` instances on specified ``Axis``. If the ``vmin`` value was explicitly set
            beforehand by the user or the ``sorting_variable`` was left unchanged, then the default value
            ``"unchanged"`` will use the same ``vmin`` value as before. However, if the ``sorting_variable`` parameter
            was changed and the ``vmin`` value was previously inferred, then by default, the global minimum will be
            re-determined for the revised ``sorting_variable`` values, as done when set to ``None``.
        :param vmax: all values greater than ``vmax`` will be set to ``vmax``. ``None`` sets as global maximum of
            feature values for all ``Node`` instances on specified ``Axis``. If the ``vmax`` value was explicitly set
            beforehand by the user or the ``sorting_variable`` was left unchanged, then the default value
            ``"unchanged"`` will use the same ``vmax`` value as before. However, if the ``sorting_variable`` parameter
            was changed and the ``vmax`` value was previously inferred, then by default, the global maximum will be
            re-determined for the revised ``sorting_variable`` values, as done when set to ``None``.
        :param start: point closest to the center of the plot (using the same positive number for multiple axes in a
            hive plot is a nice way to space out the figure). Default ``None`` maintains existing start position.
        :param end: point farthest from the center of the plot. Default ``None`` maintains existing ending position.
        :param angle: angle to set the axis, in degrees (moving counterclockwise, e.g.
            0 degrees points East, 90 degrees points North). Default ``None`` maintains existing angle.
        :param long_name: longer name for use when labeling on graph (but not for referencing the axis).
            Default ``None`` sets it to ``axis_id``. Default ``None`` maintains existing long name.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :param build_hive_plot: whether to rebuild the hive plot (i.e. redraw edges). This
            computation is usually desired, but users can save extra computation if running multiple setter methods by
            saving rebuilding for the last setter call.
        :raises AssertionError: if provided ``axis_id`` not an existing axis under the ``axes`` attribute.
        :return: ``None``.
        """
        assert axis_id in self.axes, (
            f"Provided `axis_id` ({axis_id}) not found. Must update an *existing* axis ID. "
            f"Current axis IDs are {list(self.axes.keys())}"
        )

        # default params will come from original axis settings
        axis_instantiation_params = {
            "axis_id": axis_id,
            "start": self.axes[axis_id].polar_start,
            "end": self.axes[axis_id].polar_end,
            "angle": self.axes[axis_id].angle,
            "long_name": self.axes[axis_id].long_name,
        }
        node_placement_params = {
            "axis_id": axis_id,
            "node_df": None,  # no need to update node dataframe there, just moving existing nodes
            "sorting_feature_to_use": self.axes[axis_id].sorting_variable,
            "vmin": self.axes[axis_id].vmin,
            "vmax": self.axes[axis_id].vmax,
        }

        # whether current axis vmin and vmax were inferred
        inferred_vmin = self.axes[axis_id].inferred_vmin
        inferred_vmax = self.axes[axis_id].inferred_vmax

        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        # don't bother rebuilding axis unless at least one relevant parameter is changed
        if any(i is not None for i in [start, end, angle, long_name]):
            if start is not None:
                axis_instantiation_params["start"] = start
            if end is not None:
                axis_instantiation_params["end"] = end
            if angle is not None:
                axis_instantiation_params["angle"] = angle
            if long_name is not None:
                axis_instantiation_params["long_name"] = long_name

            new_axis = Axis(**axis_instantiation_params)

            # replace old axis with new axis
            self.reset_edges(axis_id_1=axis_id)
            del self.axes[axis_id]
            self.add_axes(new_axis)

        if sorting_variable is not None:
            if sorting_variable not in self.nodes.data.columns:
                raise InvalidSortingVariableError(
                    f"Invalid `sorting_variable` ('{sorting_variable}') provided for axis {axis_id}, "
                    f"must be column of node data: {self.nodes.data.columns.to_list()}"
                )
            # old edges with axis invalid if user changed sorting variable
            self.reset_edges(axis_id_1=axis_id)
            node_placement_params["sorting_feature_to_use"] = sorting_variable
            if vmin == "unchanged" and inferred_vmin:
                node_placement_params["vmin"] = None
            if vmax == "unchanged" and inferred_vmax:
                node_placement_params["vmax"] = None
        if vmin != "unchanged":
            # old edges with axis invalid if user changed vmin
            self.reset_edges(axis_id_1=axis_id)
            node_placement_params["vmin"] = vmin
            inferred_vmin = vmin is None
        if vmax != "unchanged":
            # old edges with axis invalid if user changed vmax
            self.reset_edges(axis_id_1=axis_id)
            node_placement_params["vmax"] = vmax
            inferred_vmax = vmax is None

        # replace nodes on axis if there are allocated nodes to place
        #  otherwise just set sorting variable, vmin, and vmax
        if self.node_assignments[axis_id] is not None:
            self.place_nodes_on_axis(
                **node_placement_params,
            )
        else:
            self.axes[axis_id].set_sorting_variable(
                label=node_placement_params["sorting_feature_to_use"]
            )
        self.sorting_variables[axis_id] = node_placement_params[
            "sorting_feature_to_use"
        ]
        # update axis attributes in both cases
        self.axes[axis_id].set_node_vmin_and_vmax(
            vmin=node_placement_params["vmin"],
            vmax=node_placement_params["vmax"],
            inferred_vmin=inferred_vmin,
            inferred_vmax=inferred_vmax,
        )

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        if build_hive_plot:
            # rebuilding axes from scratch here would defeat the point of running this method
            self.build_hive_plot(
                build_axes_from_scratch=False,
                preserve_original_edge_kwargs=preserve_original_edge_kwargs,
            )
        else:
            self.warn_on_plot = True

        return

    def build_axes(
        self,
        build_axes_from_scratch: bool = False,
        preserve_original_edge_kwargs: bool = False,
    ) -> None:
        """
        Build axes and place nodes corresponding to current partition.

        :param build_axes_from_scratch: if ``True``, then all old axes and edges will be deleted and new axes will be
            generated. This is useful for example when the partition variable is changed. Note, however, that this will
            drop any existing keyword arguments modifying the axes (e.g. manually changing angles, starting and ending
            axes positions, etc.).
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :return: ``None``.
        """
        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        # remove any existing axes and edges if building from scratch
        if build_axes_from_scratch:
            self.reset_edges()
            self.axes = {}

        # space out axes evenly
        spacing = 360 / len(self.partition)

        if spacing <= self.angle_between_repeat_axes:
            warnings.warn(
                f"Your angle between repeat axes ({self.angle_between_repeat_axes}) may cause repeat axes to "
                "cross past other axes, which will lead to overlapping edges in the final Hive Plot visualization. "
                f"To space out axes equally, they are {spacing} degrees apart. "
                "We recommend setting a lower value with the `set_angle_between_repeat_axes()` method.",
                stacklevel=2,
            )

        for i, (axis_name, group) in enumerate(self.partition):
            # grab original settings if axis exists
            if axis_name in self.axes:
                # angle already respects the current self.rotation
                angle = self.axes[axis_name].angle
                sorting_variable = self.axes[axis_name].sorting_variable
                # maintain inference of vmin / vmax if previously inferred
                vmin = (
                    None
                    if self.axes[axis_name].inferred_vmin
                    else self.axes[axis_name].vmin
                )
                vmax = (
                    None
                    if self.axes[axis_name].inferred_vmax
                    else self.axes[axis_name].vmax
                )
                start = self.axes[axis_name].polar_start
                end = self.axes[axis_name].polar_end
                long_name = self.axes[axis_name].long_name

            # building axis from scratch
            else:
                angle = spacing * i + self.rotation
                sorting_variable = self.sorting_variables[axis_name]
                vmin = None
                vmax = None
                start = 1
                end = 5
                long_name = None

            repeat_axis = axis_name in self.repeat_axes

            # add axis / axes
            if not repeat_axis:
                temp_axis = Axis(
                    axis_id=axis_name,
                    start=start,
                    end=end,
                    angle=angle,
                    long_name=long_name,
                )
                # revise old axis if still there, killing edges
                if axis_name in self.axes:
                    self.reset_edges(axis_id_1=axis_name)
                else:
                    self.add_axes(temp_axis)
            else:
                repeat_axis_name = f"{axis_name}_repeat"

                # if already had the repeat axis, respect user defaults
                if repeat_axis_name in self.axes:
                    # angle already respects the current self.angle_between_repeat_axes
                    repeat_angle = self.axes[repeat_axis_name].angle
                    repeat_sorting_variable = self.axes[
                        repeat_axis_name
                    ].sorting_variable
                    # maintain inference of vmin / vmax if previously inferred
                    repeat_vmin = (
                        None
                        if self.axes[repeat_axis_name].inferred_vmin
                        else self.axes[repeat_axis_name].vmin
                    )
                    repeat_vmax = (
                        None
                        if self.axes[repeat_axis_name].inferred_vmax
                        else self.axes[repeat_axis_name].vmax
                    )
                    repeat_start = self.axes[repeat_axis_name].polar_start
                    repeat_end = self.axes[repeat_axis_name].polar_end
                    repeat_long_name = self.axes[repeat_axis_name].long_name

                # otherwise redraw both axes, shifting original axis accordingly to accommodate the repeat axis
                #  and using same values on original axis for repeat axis
                else:
                    # original axis is the same other than the angle changing to respect the addition of a repeat axis
                    angle -= self.angle_between_repeat_axes / 2
                    repeat_angle = angle + self.angle_between_repeat_axes
                    repeat_sorting_variable = self.sorting_variables[repeat_axis_name]
                    # default same span as non repeat axis if axes have same sorting variable
                    #   otherwise default span full extent of data
                    repeat_vmin = (
                        vmin
                        if self.sorting_variables[repeat_axis_name]
                        == self.sorting_variables[axis_name]
                        else None
                    )
                    repeat_vmax = (
                        vmax
                        if self.sorting_variables[repeat_axis_name]
                        == self.sorting_variables[axis_name]
                        else None
                    )
                    # default create repeat axis spanning same polar rho as non repeat axis
                    repeat_start = start
                    repeat_end = end
                    # repeat axis long name should exclude the _repeat of the axis name if newly generated
                    repeat_long_name = long_name if long_name is not None else axis_name

                # revise old axis if still there, killing edges and updating angle to accommodate repeat axis
                if axis_name in self.axes:
                    self.reset_edges(axis_id_1=axis_name)
                    self.update_axis(
                        axis_id=axis_name,
                        angle=angle,
                        build_hive_plot=False,
                    )
                else:
                    temp_axis = Axis(
                        axis_id=axis_name,
                        start=start,
                        end=end,
                        angle=angle,
                        long_name=long_name,
                    )
                    self.add_axes(temp_axis)

                if repeat_axis_name in self.axes:
                    self.reset_edges(axis_id_1=axis_name)
                else:
                    temp_axis_repeat = Axis(
                        axis_id=repeat_axis_name,
                        start=repeat_start,
                        end=repeat_end,
                        angle=repeat_angle,
                        long_name=repeat_long_name,
                    )
                    self.add_axes(temp_axis_repeat)

            # place nodes on the axis
            self.place_nodes_on_axis(
                axis_id=axis_name,
                node_df=group,
                sorting_feature_to_use=sorting_variable,
                vmin=vmin,
                vmax=vmax,
            )
            # also place values on the repeat axis if we have one
            if repeat_axis:
                self.place_nodes_on_axis(
                    axis_id=repeat_axis_name,
                    node_df=group,
                    sorting_feature_to_use=repeat_sorting_variable,
                    vmin=repeat_vmin,
                    vmax=repeat_vmax,
                )
        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        return

    def connect_adjacent_axes(
        self,
        rebuild_edges: bool = True,
        warn_on_overlapping_kwargs: Optional[bool] = None,
        preserve_original_edge_kwargs: bool = False,
    ) -> None:
        """
        Connect all adjacent axes.

        .. note::
            This function call will reset all the existing edges, redrawing all the edges from scratch.

            Calling this method will kill any changes made to edges via the
            :py:meth:`hiveplotlib.HivePlot.update_edges()` method (except for any plotting keyword arguments if
            ``preserve_original_edge_kwargs=True``).

        :param rebuild_edges: whether to only update edge kwargs or to also redraw the edges. Default ``True``
            also rebuilds edges.
        :param warn_on_overlapping_kwargs: whether to warn if overlapping keyword arguments are detected among the
            ``"all_edge_kwargs"``, ``"repeat_edge_kwargs"``, ``"clockwise_edge_kwargs"``, and
            ``"counterclockwise_edge_kwargs"`` parameters. Default ``None`` falls back to the value set by the
            ``warn_on_overlapping_kwargs`` attribute.
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        """
        # preserve original hive plot edges info so we can bring back the user-provided kwargs if desired
        original_edge_info = deepcopy(self.hive_plot_edges)

        if rebuild_edges:
            self.reset_edges()

        # get order of axes based on angles so we can add adjacent edges
        ordered_by_angle_axes = (
            pd.DataFrame(
                [(self.axes[ax].angle, self.axes[ax].axis_id) for ax in self.axes]
            )
            .sort_values(0)[1]
            .tolist()
        )

        clockwise_edge_kwargs = self.__check_for_overlapping_edge_kwargs(
            edge_kwarg_setting="clockwise_edge_kwargs",
            warn_on_overlapping_kwargs=warn_on_overlapping_kwargs,
        )
        counterclockwise_edge_kwargs = self.__check_for_overlapping_edge_kwargs(
            edge_kwarg_setting="counterclockwise_edge_kwargs",
            warn_on_overlapping_kwargs=warn_on_overlapping_kwargs,
        )
        repeat_edge_kwargs = self.__check_for_overlapping_edge_kwargs(
            edge_kwarg_setting="repeat_edge_kwargs",
            warn_on_overlapping_kwargs=warn_on_overlapping_kwargs,
        )
        # check for overlapping edge kwargs on non-repeat, but no need to store
        #  (non repeat edge kwargs will be incorporated into cw and ccw edge kwargs)
        self.__check_for_overlapping_edge_kwargs(
            edge_kwarg_setting="non_repeat_edge_kwargs",
            edge_kwargs_to_check_against=[
                "clockwise_edge_kwargs",
                "counterclockwise_edge_kwargs",
                "all_edge_kwargs",
            ],
            pairwise_checks=True,
            warn_on_overlapping_kwargs=warn_on_overlapping_kwargs,
        )

        # add in edges
        for i, axis_name in enumerate(ordered_by_angle_axes):
            # skip connecting back to first axis if only 2 axes (would be redundant)
            if len(ordered_by_angle_axes) == 2 and i == 1:
                break
            first_axis_name = axis_name

            # figure out next axis to connect to
            # else circle back to first axis
            next_axis_name = (
                ordered_by_angle_axes[i + 1]
                if i != len(ordered_by_angle_axes) - 1
                else ordered_by_angle_axes[0]
            )

            # repeat to non-repeat of same axis needs custom handling to avoid repeat edges
            #   and may include custom kwargs
            if [first_axis_name, next_axis_name] == [
                first_axis_name,
                f"{first_axis_name}_repeat",
            ]:
                # add repeat axis edges (only in ccw direction) if we have a repeat axis
                if not rebuild_edges:
                    for tag in self.edges._data:
                        self.add_edge_kwargs(
                            axis_id_1=first_axis_name,
                            axis_id_2=f"{first_axis_name}_repeat",
                            tag=tag,
                            a2_to_a1=False,  # otherwise we double the edges in this case
                            overwrite_existing_kwargs=True,
                            warn_on_no_edges=False,
                            **repeat_edge_kwargs,
                        )
                else:
                    for tag in self.edges._data:
                        self.connect_axes(
                            edges=self.edges.export_edge_array(tag=tag),
                            axis_id_1=first_axis_name,
                            axis_id_2=f"{first_axis_name}_repeat",
                            tag=tag,
                            a2_to_a1=False,  # otherwise we double the edges in this case
                            overwrite_existing_kwargs=True,
                            num_steps=self.num_steps_per_edge,
                            warn_on_no_edges=False,
                            **repeat_edge_kwargs,
                        )
            else:
                if not rebuild_edges:
                    for tag in self.edges._data:
                        self.add_edge_kwargs(
                            axis_id_1=first_axis_name,
                            axis_id_2=next_axis_name,
                            tag=tag,
                            a1_to_a2=False,
                            overwrite_existing_kwargs=True,
                            warn_on_no_edges=False,
                            **clockwise_edge_kwargs,
                        )
                        self.add_edge_kwargs(
                            axis_id_1=first_axis_name,
                            axis_id_2=next_axis_name,
                            tag=tag,
                            a2_to_a1=False,
                            overwrite_existing_kwargs=True,
                            warn_on_no_edges=False,
                            **counterclockwise_edge_kwargs,
                        )
                else:
                    for tag in self.edges._data:
                        self.connect_axes(
                            edges=self.edges.export_edge_array(tag=tag),
                            axis_id_1=first_axis_name,
                            axis_id_2=next_axis_name,
                            tag=tag,
                            a1_to_a2=False,
                            overwrite_existing_kwargs=True,
                            num_steps=self.num_steps_per_edge,
                            warn_on_no_edges=False,
                            **clockwise_edge_kwargs,
                        )
                        self.connect_axes(
                            edges=self.edges.export_edge_array(tag=tag),
                            axis_id_1=first_axis_name,
                            axis_id_2=next_axis_name,
                            tag=tag,
                            a2_to_a1=False,
                            overwrite_existing_kwargs=True,
                            num_steps=self.num_steps_per_edge,
                            warn_on_no_edges=False,
                            **counterclockwise_edge_kwargs,
                        )

        if preserve_original_edge_kwargs:
            self.__populate_original_edge_kwargs(original_edge_info=original_edge_info)

        return

    def build_hive_plot(
        self,
        build_axes_from_scratch: bool = False,
        preserve_original_edge_kwargs: bool = False,
    ) -> None:
        """
        Run all necessary computations to rebuild the underlying hive plot.

        .. note::
            Calling this method will kill any changes made to edges via the
            :py:meth:`hiveplotlib.HivePlot.update_edges()` method (except for any plotting keyword arguments if
            ``preserve_original_edge_kwargs=True``).

        :param build_axes_from_scratch: if ``True``, old axes will be deleted and new axes will be generated. This is
            useful for example when the partition variable is changed. Note, however, that this will
            drop any existing keyword arguments modifying the axes (e.g. manually changing angles, starting and ending
            axes positions, etc.).
        :param preserve_original_edge_kwargs: whether to preserve the original edge keyword arguments stored under the
            ``hive_plot_edges`` attribute.
        :return: ``None``.
        """
        self.build_axes(
            build_axes_from_scratch=build_axes_from_scratch,
            preserve_original_edge_kwargs=preserve_original_edge_kwargs,
        )
        self.connect_adjacent_axes(
            preserve_original_edge_kwargs=preserve_original_edge_kwargs,
        )
        self.warn_on_plot = False

        return

    def __check_for_overlapping_edge_kwargs(
        self,
        edge_kwarg_setting: EDGE_KWARG_HIERARCHY,
        edge_kwargs_to_check_against: Optional[list[EDGE_KWARG_HIERARCHY]] = None,
        pairwise_checks: bool = False,
        warn_on_overlapping_kwargs: Optional[bool] = None,
    ) -> Union[dict, None]:
        """
        Check the provided edge kwarg setting for redundant edge kwargs.

        Return the collective edge keyword arguments as they would compile together according to the current
        ``edge_kwarg_hierarchy`` if ``pairwise_checks`` is ``False``. Otherwise, return ``None``.

        :param edge_kwarg_setting: which setting to check for redundancies against the other kwargs.
        :param edge_kwargs_to_check_against: which edge kwargs to check against the provided setting. Default ``None``
            checks against all other possibly overlapping edge kwarg settings.
        :param pairwise_checks: whether to check the ``edge_kwarg`` setting for overlaps when collapsing the kwargs to
            a single dictionary. Default ``False`` checks for overlaps across all edge kwarg settings. ``True`` will
            check for overlaps between each (``edge_kwarg_setting``, 1 element of ``edge_kwargs_to_check_against``)
            pair.
        :param warn_on_overlapping_kwargs: whether to warn if overlapping keyword arguments are detected among the
            ``"all_edge_kwargs"``, ``"repeat_edge_kwargs"``, ``"non_repeat_edge_kwargs"``, ``"clockwise_edge_kwargs"``,
            and ``"counterclockwise_edge_kwargs"`` parameters. Default ``None`` falls back to the value set by the
            ``warn_on_overlapping_kwargs`` attribute.
        :return: the collective edge keyword arguments as they would compile together according to the current
            ``edge_kwarg_hierarchy`` if ``pairwise_checks`` is ``False``. Else, return ``None``.
        """
        if warn_on_overlapping_kwargs is not None:
            warn_on_overlapping_kwargs = self.warn_on_overlapping_kwargs
        kwargs_to_skip = []
        # repeat / clockwise / counterclockwise edge kwargs don't ever intersect, so don't check for overlap
        #  (clockwise / counterclockwise definitionally are disjoint, repeat we force to be disjoint since we choose to
        #   plot repeat edges in only one direction to avoid redundancy)
        if edge_kwarg_setting == "repeat_edge_kwargs":
            kwargs_to_skip = [
                "clockwise_edge_kwargs",
                "counterclockwise_edge_kwargs",
                "non_repeat_edge_kwargs",
            ]
        elif edge_kwarg_setting == "clockwise_edge_kwargs":
            kwargs_to_skip = [
                "repeat_edge_kwargs",
                "counterclockwise_edge_kwargs",
            ]
        elif edge_kwarg_setting == "counterclockwise_edge_kwargs":
            kwargs_to_skip = [
                "clockwise_edge_kwargs",
                "repeat_edge_kwargs",
            ]
        elif edge_kwarg_setting == "non_repeat_edge_kwargs":
            kwargs_to_skip = [
                "repeat_edge_kwargs",
            ]

        if edge_kwargs_to_check_against is None:
            edge_kwargs_to_check_against = self.edge_kwarg_hierarchy
            final_dict = {}
        else:
            final_dict = self.edge_plotting_keyword_arguments[edge_kwarg_setting]

        # track whether we ever had overlapping keys
        intersecting_keys_warnings = []
        # initialize final kwarg dict with the chosen `edge_kwarg_setting`
        #   build unify kwargs as we go, checking for clashing keys
        for k in edge_kwargs_to_check_against:
            if k not in kwargs_to_skip:
                current_keys = set(final_dict.keys())
                next_keys = set(self.edge_plotting_keyword_arguments[k].keys())

                intersection = current_keys.intersection(next_keys)
                if len(intersection) > 0:
                    w = (
                        f"Repeated kwargs {intersection} detected when setting edge kwargs for {edge_kwarg_setting}. "
                        "Preserving kwargs according to `edge_kwarg_hierarchy`"
                    )
                    intersecting_keys_warnings.append(w)
                if not pairwise_checks:
                    final_dict |= self.edge_plotting_keyword_arguments[k]
        if warn_on_overlapping_kwargs:
            for w in set(intersecting_keys_warnings):  # only show unique warnings
                warnings.warn(
                    w,
                    stacklevel=2,
                )

        if not pairwise_checks:
            return final_dict
        return None

    def update_edge_plotting_keyword_arguments(
        self,
        edge_kwarg_setting: EDGE_KWARG_HIERARCHY = "all_edge_kwargs",
        reset_edge_kwarg_setting: bool = False,
        rebuild_edges: bool = False,
        **kwargs,
    ) -> dict:
        """
        Update the edge keyword arguments for a specific ``edge_kwarg_setting``.

        :param edge_kwarg_setting: which edge kwarg setting to modify.
        :param reset_edge_kwarg_setting: whether to overwrite existing keyword arguments for the chosen
            ``edge_kwarg_setting``.
        :param rebuild_edges: whether to only update edge kwargs or to also redraw the edges. Default ``False``
            only updates edge kwargs.
        :param kwargs: additional keyword arguments to provide to the specified edge kwarg setting.
        :return: dictionary of the resulting keyword arguments for that edge kwarg setting.
        """
        if reset_edge_kwarg_setting:
            self.edge_plotting_keyword_arguments[edge_kwarg_setting] = kwargs
        else:
            self.edge_plotting_keyword_arguments[edge_kwarg_setting] |= kwargs

        if self.warn_on_overlapping_kwargs:
            self.__check_for_overlapping_edge_kwargs(
                edge_kwarg_setting=edge_kwarg_setting,
            )

        self.connect_adjacent_axes(
            rebuild_edges=rebuild_edges,
            warn_on_overlapping_kwargs=False,  # if there's a warning, it will be triggered by the above call
        )

        return self.edge_plotting_keyword_arguments[edge_kwarg_setting]

    def rename_edge_kwargs(self, **rename_kwargs) -> None:
        """
        Rename specific edge kwarg names.

        This will operate on all of the possible edge kwarg settings stored in the ``edge_plotting_keyword_arguments``
        attribute *and* edge kwargs stored in the ``hive_plot_edges`` This allows users to quickly accommodate different
        visualization back ends that may require different keyword argument names.

        .. note::
            Not all edge keyword arguments are supported by all back ends. For example, some back ends may not support
            the ``zorder`` concept in ``matplotlib`` to reorder the plotting of edges *independently of the order in
            which they were plotted. In this case, users can *remove* these keyword arguments entirely by providing
            ``{old_name: None}`` in the ``rename_kwargs`` parameter.

        :param rename_kwargs: dictionary that will map old keyword argument names to new keyword argument names.
            This will operate on all of the possible edge kwarg settings stored in the
            ``edge_plotting_keyword_arguments`` attribute *and* edge kwargs stored in the ``hive_plot_edges`` This
            allows users to quickly accommodate different visualization back ends that may require different keyword
            argument names. To remove an incompatible edge kwarg, provide ``{old_name: None}`` in the dictionary.
        """
        for old_name, new_name in rename_kwargs.items():
            # rename kwargs in edge_plotting_keyword_arguments
            for kwarg_setting in self.edge_plotting_keyword_arguments:
                if old_name in self.edge_plotting_keyword_arguments[kwarg_setting]:
                    if new_name is None:
                        del self.edge_plotting_keyword_arguments[kwarg_setting][
                            old_name
                        ]
                    else:
                        self.edge_plotting_keyword_arguments[kwarg_setting][
                            new_name
                        ] = self.edge_plotting_keyword_arguments[kwarg_setting].pop(
                            old_name
                        )
            # rename kwargs in hive_plot_edges
            for axis_id_1 in self.hive_plot_edges:
                for axis_id_2 in self.hive_plot_edges[axis_id_1]:
                    for tag in self.hive_plot_edges[axis_id_1][axis_id_2]:
                        if "edge_kwargs" in self.hive_plot_edges[axis_id_1][axis_id_2][
                            tag
                        ] and (
                            old_name
                            in self.hive_plot_edges[axis_id_1][axis_id_2][tag][
                                "edge_kwargs"
                            ]
                        ):
                            if new_name is None:
                                del self.hive_plot_edges[axis_id_1][axis_id_2][tag][
                                    "edge_kwargs"
                                ][old_name]
                            else:
                                self.hive_plot_edges[axis_id_1][axis_id_2][tag][
                                    "edge_kwargs"
                                ][new_name] = self.hive_plot_edges[axis_id_1][
                                    axis_id_2
                                ][tag]["edge_kwargs"].pop(old_name)

        self.connect_adjacent_axes(
            rebuild_edges=False,
            warn_on_overlapping_kwargs=True,
            preserve_original_edge_kwargs=True,
        )

        return

    @edge_kwarg_hierarchy.setter
    def edge_kwarg_hierarchy(
        self,
        order: Union[
            tuple,
            list[EDGE_KWARG_HIERARCHY],
        ] = (
            "all_edge_kwargs",
            "clockwise_edge_kwargs",
            "counterclockwise_edge_kwargs",
            "repeat_edge_kwargs",
            "non_repeat_edge_kwargs",
        ),
    ) -> None:
        """
        Set hierarchy of user-provided edge keyword arguments from least prioritized to most prioritized.

        .. note::
            Repeat / clockwise / counterclockwise edge keyword arguments don't ever intersect, so the relative order
            between these three settings will not affect anything.

            Clockwise / counterclockwise edges definitionally are disjoint. For repeat axes, we force these edges to
            ignore any clockwise / counterclockwise keyword arguments since we have to plot repeat edges in only one
            direction to avoid redundant plotting, and that choice of direction is arbitrary.

        :param order: Desired ordering of edge keyword arguments, where, if there are any overlapping arguments between
            the possible keyword argument options, the latter ones will be preserved over the former when plotting.
            For example, the default ordering that starts with ``"all_edge_kwargs"`` means those edge kwargs will be
            overwritten if also provided by any of ``"repeat_edge_kwargs"``, ``"clockwise_edge_kwargs"``, or
            ``"counterclockwise_edge_kwargs"``.
        :raises InvalidEdgeKwargHierarchyError: if an invalid ``order`` provided. Each key in the
            ``edge_kwarg_hierarchy`` parameter must be provided exactly once, with no other values provided.
        :return: ``None``.
        """
        order_values = set(order)
        expected_values = set(self.edge_plotting_keyword_arguments.keys())

        if order_values != expected_values or len(order) != len(
            self._edge_kwarg_hierarchy
        ):
            raise InvalidEdgeKwargHierarchyError(
                "Invalid provided `order` to `HivePlot.edge_kwarg_hierarchy`.\n"
                "All of the following values must be provided exactly once:\n"
                f"{list(self.edge_plotting_keyword_arguments.keys())}"
            )

        self._edge_kwarg_hierarchy = list(order)

        # rebuild edge kwargs accordingly
        self.connect_adjacent_axes(rebuild_edges=False)

        return

    def update_node_viz_kwargs(
        self,
        reset_kwargs: bool = False,
        **node_viz_kwargs,
    ) -> None:
        """
        Update keyword arguments for plotting nodes in a ``node_viz()`` call.

        Users can either provide values in two ways.

        1. By providing a string value corresponding to a column name, in which case that column data would be used for
        that plotting keyword argument in a ``node_viz()`` call.

        2. By providing explicit keyword arguments (e.g. ``cmap="viridis"``), in which case that keyword argument would
        be used as-is in a ``node_viz()`` call.

        .. note::
            Provided keyword argument values will be checked *first* against column names in
            ``nodes.data`` (i.e. (1) above) before falling back to (2) and setting the keyword argument
            explicitly.

            The appropriate keyword argument names should be chosen as a function of your choice of visualization back
            end (e.g. ``matplotlib``, ``bokeh``, ``datashader``, etc.).

            This is a wrapper method for calling :py:meth:`hiveplotlib.NodeCollection.update_node_viz_kwargs()` on
            the underlying ``nodes`` attribute.

        :param reset_kwargs: whether to drop the existing keyword arguments before adding the provided keyword arguments
            to the ``node_viz_kwargs`` attribute. Existing values are preserved by default (i.e.
            ``reset_kwargs=False``).
        :param node_viz_kwargs: keyword arguments to provide to a ``node_viz()`` call. Users can provide names according
            to column names in the ``data`` attribute or explicit values, as discussed in (1) and (2) above.
        :return: ``None``.
        """
        return self.nodes.update_node_viz_kwargs(
            reset_kwargs=reset_kwargs,
            **node_viz_kwargs,
        )

    def plot(self, **kwargs):  # noqa: ANN201
        """
        Plot underlying hive plot.

        .. note::
            When the backend is set to ``datashader``, any provided node plotting keyword arguments in
            ``nodes.node_viz_kwargs`` will be disregarded, as attributes like color and size are reserved for
            datashading the nodes. Inclusion of any ``node_kwargs`` here will also raise a warning.

            When the backend is set to ``datashader``, any provided edge plotting keyword arguments in
            ``edges.edge_viz_kwargs`` will be disregarded, as attributes like color and size are reserved for
            datashading the edges. Inclusion of any edge kwargs here as part of the additional ``im_kwargs`` (discussed
            further in the docstring for :py:func:`~hiveplotlib.viz.datashader.datashade_hive_plot_mpl()`) will likely
            trigger an error.

        :param kwargs: keyword arguments for the appropriate ``hive_plot_viz()`` call, depending on which viz backend is
            currently set. See the :ref:`viz-toc` module documentation for more information on
            possible arguments. Other than different backends having different names for equivalent keyword arguments,
            these should for the most part be interchangeable, with the exception of the ``datashader`` backend (see
            note above).
        :return: viz data structures, see the appropriate ``hive_plot_viz()`` call corresponding to the current viz
            backend for more information here.
        """
        if self.warn_on_plot:
            warnings.warn(
                "Intermediate changes have been made without updating the hive plot structure. "
                "Run the `build_hive_plot()` method on your `HivePlot` instance, or your hive plot visualization will "
                "likely be incorrect.",
                stacklevel=2,
            )
        if self.backend == "bokeh":
            from hiveplotlib.viz.bokeh import hive_plot_viz

        elif self.backend == "datashader":
            from hiveplotlib.viz.datashader import hive_plot_viz

        elif self.backend == "holoviews-bokeh":
            import holoviews as hv

            from hiveplotlib.viz.holoviews import hive_plot_viz

            hv.extension("bokeh")

        elif self.backend == "holoviews-matplotlib":
            import holoviews as hv

            from hiveplotlib.viz.holoviews import hive_plot_viz

            hv.extension("matplotlib")

        elif self.backend == "matplotlib":
            from hiveplotlib.viz.matplotlib import hive_plot_viz

        elif self.backend == "plotly":
            from hiveplotlib.viz.plotly import hive_plot_viz

        return hive_plot_viz(self, **kwargs)

    def to_json(self) -> str:
        """
        Return the plotting information from the axes, nodes, and edges in Cartesian space as a serialized JSON string.

        This allows users to visualize hive plots with arbitrary libraries, even outside of python.

        The dictionary structure of the resulting JSON will consist of two top-level keys:

        "axes" - contains the information for plotting each axis, plus the nodes on each axis in Cartesian space.

        "edges" - contains the information for plotting the discretized edges in Cartesian space, plus the corresponding
        *to* and *from* IDs that go with each edge, as well as any kwargs that were set for plotting each set of edges.

        .. note::
            The resulting JSON will *not* contain the additional data for the nodes or edges stored under the ``nodes``
            and ``edges`` attributes, respectively. It will only the Cartesian coordinates of the nodes and the
            discretized curves of the edges.

        :return: JSON output of axis, node, and edge information.
        """
        # axis endpoints and node placements (both in Cartesian space).
        axis_node_dict = {}

        for axis in self.axes:
            # endpoints of axis in Cartesian space
            start, end = self.axes[axis].start, self.axes[axis].end

            temp_dict = {
                "start": start,
                "end": end,
                "nodes": self.axes[axis]
                .node_placements.loc[:, [self.nodes.unique_id_column, "x", "y"]]
                .rename(columns={self.nodes.unique_id_column: "unique_id"})
                .to_dict(orient="list"),
            }
            axis_node_dict[axis] = temp_dict

        edge_info = deepcopy(self.hive_plot_edges)

        # edge ids, discretized curves (in Cartesian space), and kwargs
        for e1 in edge_info:
            for e2 in edge_info[e1]:
                for tag in edge_info[e1][e2]:
                    for i in ["ids", "curves", "edge_kwargs"]:
                        # curves have nan values, must revise to `None` then coax to list
                        if i == "curves":
                            arr = edge_info[e1][e2][tag][i]
                            split_arrays = np.split(
                                arr, np.where(np.isnan(arr[:, 0]))[0]
                            )
                            # be sure to drop the extra array at the end that is just a NaN value
                            split_arrays_str = [
                                arr[~np.isnan(arr[:, 0]), :].astype("O")
                                for arr in split_arrays
                            ][:-1]
                            split_arrays_list = [
                                arr.tolist() for arr in split_arrays_str
                            ]
                            edge_info[e1][e2][tag][i] = split_arrays_list
                        # ids don't have nan values, can be converted to list right away
                        elif i == "ids":
                            edge_info[e1][e2][tag][i] = edge_info[e1][e2][tag][
                                i
                            ].tolist()
                        elif i == "edge_kwargs":
                            # do same edge kwarg gathering as viz calls to aggregate kwargs in ``edges`` attribute
                            if self.edges is not None:
                                # priority queue of edge kwargs
                                final_edge_kwargs = (
                                    self.edges.edge_viz_kwargs[tag]
                                    | self.hive_plot_edges[e1][e2][tag]["edge_kwargs"]
                                )
                                # if any kwarg value corresponds to an edge data column name, use the edge data values
                                for kw, val in final_edge_kwargs.items():
                                    # if value is name of column, then propagate those values as a 1d array
                                    #  (e.g. value per edge)
                                    if (
                                        isinstance(val, Hashable)
                                        and val in self.edges._data[tag].columns
                                    ):
                                        relevant_edges = self.edges.relevant_edges[e1][
                                            e2
                                        ][tag]
                                        final_edge_kwargs[kw] = (
                                            self.edges._data[tag]
                                            .loc[relevant_edges, val]
                                            .to_list()
                                        )
                                    # otherwise pass on the kwarg normally
                                    else:
                                        final_edge_kwargs[kw] = val
                                # add kwargs into edge info
                                edge_info[e1][e2][tag][i] = final_edge_kwargs

        collated_output = {"axes": axis_node_dict, "edges": edge_info}

        return json.dumps(collated_output)


def hive_plot_n_axes(
    edges: Union[np.ndarray, List[np.ndarray]],
    axes_assignments: List[List[Union[Hashable, None]]],
    sorting_variables: List[Hashable],
    nodes: Union[NodeCollection, List[Node]] = None,
    node_list: list[Node] = None,
    axes_names: Optional[List[Hashable]] = None,
    repeat_axes: Optional[List[bool]] = None,
    vmins: Optional[List[float]] = None,
    vmaxes: Optional[List[float]] = None,
    angle_between_repeat_axes: float = 40,
    orient_angle: float = 0,
    all_edge_kwargs: Optional[Dict] = None,
    edge_list_kwargs: Optional[List[Dict]] = None,
    cw_edge_kwargs: Optional[Dict] = None,
    ccw_edge_kwargs: Optional[Dict] = None,
    repeat_edge_kwargs: Optional[Dict] = None,
    suppress_deprecation_warning: bool = False,
) -> BaseHivePlot:
    """
    Generate a ``BaseHivePlot`` Instance with an arbitrary number of axes, specified by passing a partition of node IDs.

    DEPRECATED. This function is being deprecated in favor of the revised ``HivePlot`` class. This function will be
    removed in version ``0.28.0``.

    Repeat axes can be generated for any desired subset of axes, but repeat axes will be sorted by the same variable
    as the original axis.

    Axes will be added in counterclockwise order.

    Axes will all be the same length and position from the origin.

    Changes to all the edge kwargs can be affected with the ``all_edge_kwargs`` parameter. If providing multiple sets
    of edges (e.g. a ``list`` input for the ``edges`` parameter), one can also provide unique kwargs for each set of
    edges by specifying a corresponding ``list`` of kwargs with the ``edge_list_kwargs`` parameter.

    Edges directed counterclockwise will be drawn as solid lines by default. Clockwise edges will be drawn as solid
    lines by default. All CW / CCW lines kwargs can be changed with the ``cw_edge_kwargs`` and ``ccw_edge_kwargs``
    parameters, respectively. Edges between repeat axes will be drawn as solid lines by default. Repeat edges operate
    under their own set of visual kwargs (``repeat_edge_kwargs``) as clockwise vs counterclockwise edges don't have much
    meaning when looking within a single group.

    Specific edge kwargs can also be changed by running the ``add_edge_kwargs()`` method on the resulting ``HivePlot``
    instance, where the specified ``tag`` of ``edges`` to change will be the index value in the list of
    lists in ``edges`` (note: a tag is only necessary if the ``indices`` input is a list of lists, otherwise there
    would only be a single tag of edges, which can be inferred).

    There is a hierarchy to these various kwarg arguments. That is, if redundant / overlapping kwargs are provided for
    different kwarg parameters, a warning will be raised and priority will be given according to the below hierarchy
    (Note: ``cw_edge_kwargs, ``ccw_edge_kwargs``, and ``repeat_edge_kwargs`` do not interact with each other in
    practice, and are therefore equal in the hierarchy):

    ``edge_list_kwargs`` > ``cw_edge_kwargs`` / ``ccw_edge_kwargs`` / ``repeat_edge_kwargs`` > ``all_edge_kwargs``.

    :param nodes: ``NodeCollection`` or list of ``Node`` instances to go into output ``BaseHivePlot`` instance. Must
        provide only one of ``nodes`` or ``node_list``.
    :param node_list: List of ``Node`` instances to go into output ``BaseHivePlot`` instance. Must provide only one of
        ``nodes`` or ``node_list``.
    :param edges: ``(n, 2)`` array of ``Hashable`` values representing pointers to specific ``Node`` instances.
        The first column is the "from" and the second column is the "to" for each connection.
        Alternatively, one can provide a list of two-column arrays, which will allow for plotting different sets of
        edges with different kwargs.
    :param axes_assignments: list of lists of node unique IDs. Each list of node IDs will be assigned to a separate axis
        in the resulting ``BaseHivePlot`` instance, built out in counterclockwise order. If ``None`` is provided as one
        of the elements instead of a list of node IDs, then all unassigned nodes will be aggregated onto this axis.
    :param sorting_variables: list of ``Hashable`` variables on which to sort each axis, where the ith index
        ``Hashable`` corresponds to the ith index list of nodes in ``axes_assignments`` (e.g. the ith axis of the
        resulting ``BaseHivePlot``).
    :param axes_names: list of ``Hashable`` names for each axis, where the ith index ``Hashable`` corresponds to the ith
        index list of nodes in ``axes_assignments`` (e.g. the ith axis of the resulting ``BaseHivePlot``). Default
        ``None`` names the groups as "Group 1," "Group 2," etc.
    :param repeat_axes: list of ``bool`` values of whether to generate a repeat axis, where the ith index bool
        corresponds to the ith index list of nodes in ``axes_assignments`` (e.g. the ith axis of the resulting
        ``HivePlot``). A ``True`` value generates a repeat axis. Default ``None`` assumes no repeat axes (e.g. all
        ``False``).
    :param vmins: list of ``float`` values (or ``None`` values) specifying the vmin for each axis, where the ith index
        value corresponds to the ith index list of nodes in ``axes_assignments`` (e.g. the ith axis of the resulting
        ``BaseHivePlot``). A ``None`` value infers the global min for that axis. Default ``None`` uses the global min
        for all the axes.
    :param vmaxes: list of ``float`` values (or ``None`` values) specifying the vmax for each axis, where the ith index
        value corresponds to the ith index list of nodes in ``axes_assignments`` (e.g. the ith axis of the resulting
        ``BaseHivePlot``). A ``None`` value infers the global max for that axis. Default ``None`` uses the global max
        for all the axes.
    :param angle_between_repeat_axes: angle between repeat axes. Default 40 degrees.
    :param orient_angle: rotates all axes counterclockwise from their initial angles (default 0 degrees).
    :param all_edge_kwargs: kwargs for all edges. Default ``None`` specifies no additional kwargs.
    :param edge_list_kwargs: list of dictionaries of kwargs for each element of ``edges`` when ``edges`` is a ``list``.
        The ith set of kwargs in ``edge_list_kwargs`` will only be applied to edges constructed from the ith element of
        ``edges``. Default ``None`` provides no additional kwargs. Note, list must be same length as ``edges``.
    :param cw_edge_kwargs: kwargs for edges going clockwise. Default ``None`` specifies a solid line.
    :param ccw_edge_kwargs: kwargs for edges going counterclockwise. Default ``None`` specifies a solid line.
    :param repeat_edge_kwargs: kwargs for edges between repeat axes. Default ``None`` specifies a solid line.
    :param suppress_deprecation_warning: whether to suppress the ``DeprecationWarning``.
    :return: ``BaseHivePlot`` instance.
    """
    if not suppress_deprecation_warning:  # pragma: no cover
        warnings.warn(
            "hive_plot_n_axes is being deprecated in favor of the revised HivePlot class. "
            "It will be removed in v0.28.0.",
            category=DeprecationWarning,
            stacklevel=2,
        )
    assert nodes is None or node_list is None, (
        "Only provide one of  `node_list` parameter or `nodes`."
    )
    if node_list is not None:  # pragma: no cover
        nodes = node_collection_from_node_list(node_list=node_list)
    # make sure kwarg arguments are correct
    if all_edge_kwargs is None:
        all_edge_kwargs = {}

    if isinstance(edges, list):
        if edge_list_kwargs is not None:
            assert len(edges) == len(edge_list_kwargs), (
                f"Must provide same number of sets of edges (currently len(edges) = {len(edges)}) as edge kwargs"
                f"(currently len(edge_list_kwargs) = {len(edge_list_kwargs)}"
            )
            for idx, k in enumerate(edge_list_kwargs):
                if k is None:
                    edge_list_kwargs[idx] = {}
        else:
            edge_list_kwargs = [{} for _ in edges]
    else:
        edge_list_kwargs = [{}]

    if cw_edge_kwargs is None:
        cw_edge_kwargs = {}
    if ccw_edge_kwargs is None:
        ccw_edge_kwargs = {}
    if repeat_edge_kwargs is None:
        repeat_edge_kwargs = {}
    # make sure specified instructions match the number of specified axes
    assert len(axes_assignments) == len(sorting_variables), (
        "Must specify a sorting variable (`sorting_variables`) for every axis (`axes_assignments`). "
        f"Currently have {len(sorting_variables)} sorting variables and {len(axes_assignments)} axes assignments."
    )

    if axes_names is not None:
        assert len(axes_assignments) == len(axes_names), (
            "Must specify a axis name (`axes_names`) for every axis (`axes_assignments`). "
            f"Currently have {len(axes_names)} axes names and {len(axes_assignments)} axes assignments."
        )

    else:
        axes_names = [f"Group {i + 1}" for i in range(len(axes_assignments))]

    if repeat_axes is not None:
        assert len(axes_assignments) == len(repeat_axes), (
            "Must specify a repeat axis (`repeat_axes`) for every axis (`axes_assignments`). "
            f"Currently have {len(repeat_axes)} repeat axes specified and {len(axes_assignments)} axes assignments."
        )
    else:
        repeat_axes = [False] * len(axes_assignments)

    if vmins is not None:
        assert len(axes_assignments) == len(vmins), (
            "Must specify a vmin (`vmins`) for every axis (`axes_assignments`). "
            f"Currently have {len(vmins)} vmins specified and {len(axes_assignments)} axes assignments."
        )
    else:
        vmins = [None] * len(axes_assignments)

    if vmaxes is not None:
        assert len(axes_assignments) == len(vmaxes), (
            "Must specify a vmax (`vmaxes`) for every axis (`axes_assignments`). "
            f"Currently have {len(vmaxes)} vmaxes specified and {len(axes_assignments)} axes assignments."
        )
    else:
        vmaxes = [None] * len(axes_assignments)

    hp = BaseHivePlot()
    hp.add_nodes(nodes=nodes)

    # space out axes evenly
    spacing = 360 / len(axes_assignments)

    if spacing <= angle_between_repeat_axes:
        warnings.warn(
            f"Your angle between repeat axes ({angle_between_repeat_axes}) is going to cause repeat axes to cross "
            "past other axes, which will lead to overlapping edges in the final Hive Plot visualization. "
            f"To space out axes equally, they are {spacing} degrees apart. "
            "We recommend setting a lower value for `angle_between_repeat_axes`.",
            stacklevel=2,
        )

    # if we get a `None` axis assignment, assign those nodes to be the diff of all node IDs minus the assigned nodes
    none_in_axes_assignments = False
    for a in axes_assignments:
        if a is None:
            none_in_axes_assignments = True
    if none_in_axes_assignments:
        all_node_ids = nodes.data[nodes.unique_id_column].to_numpy()
        nodes_placed = []
        for nlist in axes_assignments:
            if nlist is not None:
                nodes_placed += list(nlist)

        none_axes_assignment = list(set(all_node_ids).difference(nodes_placed))
        for i, nlist in enumerate(axes_assignments):
            if nlist is None:
                axes_assignments[i] = none_axes_assignment

    for i, assignment in enumerate(axes_assignments):
        angle = spacing * i
        sorting_variable = sorting_variables[i]
        axis_name = axes_names[i]
        repeat_axis = repeat_axes[i]
        vmin = vmins[i]
        vmax = vmaxes[i]

        # add axis / axes
        if not repeat_axis:
            temp_axis = Axis(
                axis_id=axis_name, start=1, end=5, angle=angle + orient_angle
            )
            hp.add_axes(temp_axis)
        else:
            # space out on either side of the well-spaced angle
            temp_axis = Axis(
                axis_id=axis_name,
                start=1,
                end=5,
                angle=angle - angle_between_repeat_axes / 2 + orient_angle,
            )
            temp_axis_repeat = Axis(
                axis_id=f"{axis_name}_repeat",
                start=1,
                end=5,
                angle=angle + angle_between_repeat_axes / 2 + orient_angle,
                long_name=axis_name,
            )
            hp.add_axes([temp_axis, temp_axis_repeat])

        # place nodes on the axis / axes
        hp.place_nodes_on_axis(
            axis_id=axis_name,
            node_df=nodes.data.loc[
                nodes.data[nodes.unique_id_column].isin(assignment), :
            ],
            sorting_feature_to_use=sorting_variable,
            vmin=vmin,
            vmax=vmax,
        )
        # also place values on the repeat axis if we have one
        if repeat_axis:
            hp.place_nodes_on_axis(
                axis_id=f"{axis_name}_repeat",
                node_df=nodes.data.loc[
                    nodes.data[nodes.unique_id_column].isin(assignment), :
                ],
                sorting_feature_to_use=sorting_variable,
                vmin=vmin,
                vmax=vmax,
            )

    # add in edges
    if not isinstance(edges, list):
        edges = [edges]
    for i, axis_name in enumerate(axes_names):
        first_axis_name = axis_name

        # figure out next axis to connect to
        # else circle back to first axis
        next_axis_name = (
            axes_names[i + 1] if i != len(axes_names) - 1 else axes_names[0]
        )

        # repeat axis kwarg handling and connecting
        if repeat_axes[i]:
            for idx, e in enumerate(edges):
                # gather kwargs according to hierarchy
                collated_kwargs = edge_list_kwargs[idx].copy()
                for k in list(repeat_edge_kwargs.keys()):
                    if k in collated_kwargs:
                        warnings.warn(
                            f"Specified kwarg {k} in `repeat_edge_kwargs` but already set as kwarg for "
                            f"edge set index {idx} with `edge_list_kwargs`. Preserving kwargs in `edge_list_kwargs`",
                            stacklevel=2,
                        )
                    else:
                        collated_kwargs[k] = repeat_edge_kwargs[k]
                for k in list(all_edge_kwargs.keys()):
                    if k in collated_kwargs:
                        warnings.warn(
                            f"Specified kwarg {k} in `all_edge_kwargs` but already set as kwarg for "
                            f"edge set index {idx} with `edge_list_kwargs` or `repeat_edge_kwargs`. "
                            f"Disregarding `all_edge_kwargs` here.",
                            stacklevel=2,
                        )
                    else:
                        collated_kwargs[k] = all_edge_kwargs[k]

                # add repeat axis edges (only in ccw direction) if we have a repeat axis
                hp.connect_axes(
                    edges=e,
                    axis_id_1=first_axis_name,
                    axis_id_2=f"{first_axis_name}_repeat",
                    a2_to_a1=False,
                    warn_on_no_edges=False,
                    **collated_kwargs,
                )
                # the following intergroup edges will instead come off of the repeat edge
            first_axis_name += "_repeat"

        for idx, e in enumerate(edges):
            # gather kwargs according to hierarchy
            collated_kwargs_cw = edge_list_kwargs[idx].copy()
            for k in list(cw_edge_kwargs.keys()):
                if k in collated_kwargs_cw:
                    warnings.warn(
                        f"Specified kwarg {k} in `cw_edge_kwargs` but already set as kwarg for "
                        f"edge set index {idx} with `edge_list_kwargs`. Preserving kwargs in `edge_list_kwargs`",
                        stacklevel=2,
                    )
                else:
                    collated_kwargs_cw[k] = cw_edge_kwargs[k]
            for k in list(all_edge_kwargs.keys()):
                if k in collated_kwargs_cw:
                    warnings.warn(
                        f"Specified kwarg {k} in `all_edge_kwargs` but already set as kwarg for "
                        f"edge set index {idx} with `edge_list_kwargs` or `cw_edge_kwargs`. "
                        f"Disregarding `all_edge_kwargs` here.",
                        stacklevel=2,
                    )
                else:
                    collated_kwargs_cw[k] = all_edge_kwargs[k]

            hp.connect_axes(
                edges=e,
                axis_id_1=first_axis_name,
                axis_id_2=next_axis_name,
                a1_to_a2=False,
                warn_on_no_edges=False,
                **collated_kwargs_cw,
            )

            # gather kwargs according to hierarchy
            collated_kwargs_ccw = edge_list_kwargs[idx].copy()
            for k in list(ccw_edge_kwargs.keys()):
                if k in collated_kwargs_ccw:
                    warnings.warn(
                        f"Specified kwarg {k} in `ccw_edge_kwargs` but already set as kwarg for "
                        f"edge set index {idx} with `edge_list_kwargs`. Preserving kwargs in `edge_list_kwargs`",
                        stacklevel=2,
                    )
                else:
                    collated_kwargs_ccw[k] = ccw_edge_kwargs[k]
            for k in list(all_edge_kwargs.keys()):
                if k in collated_kwargs_ccw:
                    warnings.warn(
                        f"Specified kwarg {k} in `all_edge_kwargs` but already set as kwarg for "
                        f"edge set index {idx} with `edge_list_kwargs` or `ccw_edge_kwargs."
                        f"Disregarding `all_edge_kwargs` here.",
                        stacklevel=2,
                    )
                else:
                    collated_kwargs_ccw[k] = all_edge_kwargs[k]

            hp.connect_axes(
                edges=e,
                axis_id_1=first_axis_name,
                axis_id_2=next_axis_name,
                a2_to_a1=False,
                warn_on_no_edges=False,
                **collated_kwargs_ccw,
            )

    return hp
