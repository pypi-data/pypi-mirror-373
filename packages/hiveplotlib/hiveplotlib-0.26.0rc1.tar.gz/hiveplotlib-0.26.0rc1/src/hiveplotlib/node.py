# node.py

"""
Definition of ``Node`` instance and helper static methods for generating and working with ``Node`` instances.
"""

import uuid
from typing import Dict, Hashable, List, Optional, Union

import numpy as np
import pandas as pd

from hiveplotlib.exceptions import InvalidPartitionVariableError
from hiveplotlib.exceptions.node import RepeatUniqueNodeIDsError


class Node:
    """
    ``Node`` instances hold the data for individual network node.

    Each instance is initialized with a ``unique_id`` for identification. These IDs must be ``Hashable``.
    One can also initialize with a dictionary of ``data``, but data can also be added later with the ``add_data()``
    method.

    :example:

        .. highlight:: python
        .. code-block:: python

            my_node = Node(unique_id="my_unique_node_id", data=my_dataset)

            my_second_node = Node(unique_id="my_second_unique_node_id")
            my_second_node.add_data(data=my_second_dataset)
    """

    def __init__(self, unique_id: Hashable, data: Optional[Dict] = None) -> None:
        """
        Initialize ``Node`` instance.

        :param unique_id: identifier for the instance (intended to be unique).
        :param data: dictionary of data.
        """
        self.unique_id = unique_id
        self.data = {}
        if data is None:
            data = {}
        self.add_data(data, overwrite_old_data=True)
        # Hashable value that points to which `Axis` instance the node is assigned to
        #  (this will point to an `Axis` instance via `HivePlot.axes[label]`)
        self.axis_label = None

    def __repr__(self) -> str:
        """
        Make printable representation (repr) for ``Node`` instance.
        """
        return f"hiveplotlib.Node {self.unique_id}"

    def add_data(self, data: Dict, overwrite_old_data: bool = False) -> None:
        """
        Add dictionary of data to ``Node.data``.

        :param data: dict of data to associate with ``Node`` instance.
        :param overwrite_old_data: whether to delete existing data dict and overwrite with ``data``. Default ``False``.
        :return: ``None``.
        """
        assert isinstance(data, dict), "`data` must be dictionary."

        if overwrite_old_data:
            self.data = data

        else:
            for k in data:
                self.data[k] = data[k]


class NodeCollection:
    """
    Multi-node data aggregator and partitioner for downstream hive plots.

    Ingests an input ``pandas.DataFrame`` (``data``) with specification for which data column correponds to the nodes'
    unique IDs (``unique_id_column``).

    Users can provide node-plotting keyword arguments via the ``node_viz_kwargs`` parameter in two ways.

    1. By providing a string value corresponding to a column name, in which case that column data would be used for
    that plotting keyword argument in a ``node_viz()`` call.

    2. By providing explicit keyword arguments (e.g. ``cmap="viridis"``), in which case that keyword argument would
    be used as-is in a ``node_viz()`` call.

    ``node_kwargs`` can also be updated (or overwritten) after instantiation via the
    :py:meth:`~hiveplotlib.NodeCollection.update_node_viz_kwargs()` method.

    .. note::
        Provided keyword argument values will be checked *first* against column names in
        ``NodeCollection.data`` (i.e. (1) above) before falling back to (2) and setting the keyword argument
        explicitly.

        The appropriate keyword argument names should be chosen as a function of your choice of visualization back
        end (e.g. ``matplotlib``, ``bokeh``, ``datashader``, etc.).


    :param data: dataframe of node data.
    :param unique_id_column: which column of ``data`` to use for each node's unique ID. Default ``None`` creates one
        using the dataframe's index values.
    :param node_viz_kwargs: keyword arguments to provide to a ``node_viz()`` call. Users can provide names according
        to column names in the ``data`` attribute or explicit values, as discussed in (1) and (2) above.
    :param check_uniqueness: whether to check the ``unique_id_column`` of ``data`` for uniqueness. This is always good
        to check, but users may wish to skip if working with large datasets that have already checked this column for
        uniqueness, for example, if using data from a SQL database with the primary key column.
    :raises RepeatUniqueNodeIDsError: if ``data`` contains non-unique node IDs in the ``unique_id_column`` (and
        ``check_uniqueness=True``).
    """

    def __repr__(self) -> str:
        """
        Make printable representation (repr) for ``NodeCollection`` instance.
        """
        return (
            f"hiveplotlib.NodeCollection of {self.data.shape[0]} nodes "
            f"and unique ID column '{self.unique_id_column}'."
        )

    def __len__(self) -> int:
        """
        Allow ``len()`` to correspond to the number of nodes in the ``NodeCollection``.

        :return: number of nodes (i.e. rows) in ``NodeCollection.data``.
        """
        return self.data.shape[0]

    def __init__(
        self,
        data: pd.DataFrame,
        unique_id_column: Optional[Hashable] = None,
        node_viz_kwargs: Optional[dict] = None,
        check_uniqueness: bool = True,
    ) -> None:
        """Initialize."""
        # TODO: keep an `data_subset` attribute distinct from `data`. This will support plotting node subsets
        # TODO: keep an `data_highlight` attribute distinct from `data`. This will support highlighting nodes in plot
        self.data = data.copy()
        self.original_unique_id_column = unique_id_column
        # use index if no unique ID column provided
        #  make a unique index column because downstream HivePlot needs a column of index data
        if unique_id_column is None:
            unique_id_column = (
                "index_values"
                if "index_values" not in data.columns
                else f"index_values_{uuid.uuid4()}"
            )
            self.data[unique_id_column] = self.data.index.to_numpy()
        self.unique_id_column = unique_id_column
        self.check_uniqueness = check_uniqueness
        if check_uniqueness and (
            len(np.unique(self.data[self.unique_id_column].values))
            != self.data.shape[0]
        ):
            raise RepeatUniqueNodeIDsError(
                "Found repeat unique IDs:\n"
                f"{self.data[self.data.duplicated(subset=self.unique_id_column, keep=False)]}"
            )
        self.node_viz_kwargs = {} if node_viz_kwargs is None else node_viz_kwargs.copy()

    def copy(self) -> "NodeCollection":
        """
        Create a deep copy of the ``NodeCollection`` instance.

        :return: deep copy of the ``NodeCollection`` instance.
        """
        return NodeCollection(
            data=self.data.copy(),
            unique_id_column=self.unique_id_column,
            node_viz_kwargs=self.node_viz_kwargs.copy(),
            check_uniqueness=self.check_uniqueness,
        )

    def create_partition_variable(
        self,
        data_column: Hashable,
        cutoffs: Optional[Union[List[float], int]] = 3,
        labels: Optional[List[Hashable]] = None,
        partition_variable_name: Optional[Hashable] = None,
    ) -> Hashable:
        r"""
        Create a column in the ``data`` attribute partitioning the data with respect to a single column variable.

        By default, splits will partition nodes by *unique values* of ``data_column``.

        If ``data_column`` corresponds to numerical data, and a ``list`` of ``cutoffs``
        is provided, node IDs will be separated into bins according to the following binning scheme:

        (-inf, ``cutoff[0]``], (``cutoff[0]``, ``cutoff[1]``], ... , (``cutoff[-1]``, inf]

        If ``data_column`` corresponds to numerical data, and ``cutoffs`` is provided as an ``int``, node IDs will be
        separated into ``cutoffs`` equal-sized quantiles.

        .. note::
            This method currently only supports splits where ``data_column`` corresponds to *numerical* data.

        :param data_column: which column of data in the underlying ``data`` attribute to use to partition the data.
        :param cutoffs: cutoffs to use in binning nodes according to data under ``data_column``. Default ``3`` will
            bin nodes into 3 equally-sized bins based on the unique values of ``data_column``. When provided as an
            ``int``, the exact numerical break points will be determined to create ``cutoffs`` equally-sized quantiles.
            When provided as a ``list``, the specified cutoffs will bin according to
            (-inf, ``cutoffs[0]``], (``cutoffs[0]``, ``cutoffs[1]``], ... , (``cutoffs[-1]``, inf).
        :param labels: labels assigned to each bin. Only referenced when ``cutoffs`` is not ``None``. Default ``None``
            labels each bin as a string based on its range of values. Note, when ``cutoffs`` is a list, ``len(labels)``
            must be 1 greater than ``len(cutoffs)``. When ``cutoffs`` is an ``int``, ``len(labels)`` must be equal to
            ``cutoffs``.
        :param partition_variable_name: name of the resulting partition variable to add to the ``data`` attribute.
            Default ``None`` creates names starting at ``"partition_0"``, incrementing the integer to keep names unique
            if the user creates multiple partitions.
        :return: column name of partition information added to the ``data`` attribute.
        :raises InvalidPartitionVariableError: if invalid ``data_column`` provided.
        :raises InvalidPartitionVariableError: if ``partition_variable_name`` ends in ``_collapsed_axis``. This is a
            protected name for internal use.
        """
        if data_column not in self.data.columns:
            raise InvalidPartitionVariableError(
                f"Invalid `partition_variable` ({data_column}) provided, "
                f"must be column of node data: {self.data.columns.to_list()}"
            )
        if partition_variable_name is None:
            i = 0
            # keep trying new names til we get a unique one
            while True:
                partition_variable_name = f"partition_{i}"
                if partition_variable_name not in self.data.columns:
                    break
                i += 1
        else:
            if partition_variable_name.endswith("_collapsed_axis"):
                raise InvalidPartitionVariableError(
                    "Cannot use partition variable name ending in `_collapsed_axis`."
                )

        # int cutoffs dictates quantile cut, otherwise cut
        if not isinstance(cutoffs, int):
            if labels is not None:
                assert len(labels) == len(cutoffs) + 1, (
                    "Must have 1 more label than `cutoffs` (n cutoffs => n + 1 bins)"
                )

            bins = [-np.inf, *cutoffs, np.inf]
            # create pandas categorical array with binning information
            node_bin_cuts = pd.cut(
                self.data[data_column].to_numpy(), bins=bins, labels=labels
            )
        else:
            if labels is not None:
                assert len(labels) == cutoffs, (
                    "Must have 1 label per `cutoffs` (n quantiles => n labels)"
                )

            node_bin_cuts = pd.qcut(
                self.data[data_column].to_numpy(), q=cutoffs, labels=labels
            )

        # convert to np array with shape `len(node_list)` whose values are bin assignments (labels)
        node_bin_assignments = node_bin_cuts.to_numpy()

        self.data[partition_variable_name] = node_bin_assignments

        return partition_variable_name

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
            ``NodeCollection.data`` (i.e. (1) above) before falling back to (2) and setting the keyword argument
            explicitly.

            The appropriate keyword argument names should be chosen as a function of your choice of visualization back
            end (e.g. ``matplotlib``, ``bokeh``, ``datashader``, etc.).

        :param reset_kwargs: whether to drop the existing keyword arguments before adding the provided keyword arguments
            to the ``node_viz_kwargs`` attribute. Existing values are preserved by default (i.e.
            ``reset_kwargs=False``).
        :param node_viz_kwargs: keyword arguments to provide to a ``node_viz()`` call. Users can provide names according
            to column names in the ``data`` attribute or explicit values, as discussed in (1) and (2) above.
        :return: ``None``.
        """
        if reset_kwargs:
            self.node_viz_kwargs = node_viz_kwargs
        else:
            self.node_viz_kwargs |= node_viz_kwargs
        return


def node_collection_from_node_list(
    node_list: List[Node],
    unique_id_name: str = "unique_id",
    check_uniqueness: bool = True,
) -> NodeCollection:
    """
    Create :py:class:`hiveplotlib.NodeCollection` from list of :py:class:`hiveplotlib.Node` instances.

    :param node_list: list of ``Node`` instances to convert into a ``NodeCollection``.
    :param unique_id_name: name to use for unique IDs.
    :param check_uniqueness: whether or not to check that provided ``Node`` instances have unique IDs.
    :return: the resulting ``NodeCollection``.
    """
    df = pd.concat(
        [
            pd.DataFrame.from_dict(
                node.data, orient="index", columns=[node.unique_id]
            ).T
            for node in node_list
        ]
    )
    df = df.reset_index(names=unique_id_name)

    return NodeCollection(
        data=df, unique_id_column=unique_id_name, check_uniqueness=check_uniqueness
    )


def split_nodes_on_variable(
    node_list: Union[NodeCollection, List[Node]],
    variable_name: Hashable,
    cutoffs: Optional[Union[List[float], int]] = None,
    labels: Optional[List[Hashable]] = None,
) -> Dict[Hashable, List[Node]]:
    r"""
    Split a ``list`` of ``Node`` instances into a partition of node IDs.

    By default, splits will group node IDs on *unique values* of ``variable_name``.

    If ``variable_name`` corresponds to numerical data, and a ``list`` of ``cutoffs``
    is provided, node IDs will be separated into bins according to the following binning scheme:

    (-inf, ``cutoff[0]``], (``cutoff[0]``, ``cutoff[1]``], ... , (``cutoff[-1]``, inf]

    If ``variable_name`` corresponds to numerical data, and ``cutoffs`` is provided as an ``int``, node IDs will be
    separated into ``cutoffs`` equal-sized quantiles.

    .. note::
        This method currently only supports splits where ``variable_name`` corresponds to *numerical* data.

    :param node_list: list of ``Node`` instances to partition.
    :param variable_name: which variable in each ``Node`` instances to group by.
    :param cutoffs: cutoffs to use in binning nodes according to data under ``variable_name``. Default ``None`` will bin
        nodes by unique values of ``variable_name``. When provided as a ``list``, the specified cutoffs will bin
        according to (-inf, ``cutoffs[0]``], `(`cutoffs[0]``, ``cutoffs[1]``], ... , (``cutoffs[-1]``, inf).
        When provided as an ``int``, the exact numerical break points will be determined to create ``cutoffs``
        equally-sized quantiles.
    :param labels: labels assigned to each bin. Only referenced when ``cutoffs`` is not ``None``. Default ``None``
        labels each bin as a string based on its range of values. Note, when ``cutoffs`` is a list, ``len(labels)`` must
        be 1 greater than ``len(cutoffs)``. When ``cutoffs`` is an ``int``, ``len(labels)`` must be equal to
        ``cutoffs``.
    :return: ``dict`` whose values are lists of ``Node`` unique IDs. If ``cutoffs`` is ``None``, keys will be the unique
        values for the variable. Otherwise, each key will be the string representation of a bin range.
    """
    if cutoffs is None:
        output = {}
        for node in node_list:
            val = node.data[variable_name]
            if val not in output:
                output[val] = []

            output[val].append(node.unique_id)

        return output

    data_dict = {}
    for node in node_list:
        data_dict[node.unique_id] = node.data[variable_name]

    # int cutoffs dictates quantile cut, otherwise cut
    if not isinstance(cutoffs, int):
        if labels is not None:
            assert len(labels) == len(cutoffs) + 1, (
                "Must have 1 more label than `cutoffs` (n cutoffs => n + 1 bins)"
            )

        bins = [-np.inf, *cutoffs, np.inf]
        # create pandas categorical array with binning information
        node_bin_cuts = pd.cut(list(data_dict.values()), bins=bins, labels=labels)
    else:
        if labels is not None:
            assert len(labels) == cutoffs, (
                "Must have 1 label per `cutoffs` (n quantiles => n labels)"
            )

        node_bin_cuts = pd.qcut(list(data_dict.values()), q=cutoffs, labels=labels)

    # convert to np array with shape `len(node_list)` whose values are bin assignments (labels)
    node_bin_assignments = node_bin_cuts.to_numpy().astype(str)

    output = {}
    for i, node in enumerate(node_list):
        val = node_bin_assignments[i]
        if val not in output:
            output[val] = []

        output[val].append(node.unique_id)

    return output


def dataframe_to_node_list(df: pd.DataFrame, unique_id_column: Hashable) -> List[Node]:
    """
    Convert a dataframe into ``Node`` instances, where each *row* will be turned into a single instance.

    :param df: dataframe to use to generate ``Node`` instances.
    :param unique_id_column: which column corresponds to unique IDs for the eventual nodes.
    :return: list of ``Node`` instances.
    """
    assert (
        df[unique_id_column].to_numpy().size
        == np.unique(df[unique_id_column].to_numpy()).size
    ), (
        "Param `unique_id_column` contains non-unique values, cannot be used as unique IDs for nodes"
    )

    additional_data = df.drop(columns=unique_id_column).to_dict(orient="records")

    return [
        Node(unique_id=val, data=additional_data[i])
        for i, val in enumerate(df[unique_id_column].to_numpy())
    ]


def subset_node_collection_by_unique_ids(
    node_collection: NodeCollection,
    ids: Union[List[Hashable], Hashable],
) -> pd.DataFrame:
    """
    Subset ``NodeCollection`` dataframe by specific unique IDs.

    :param node_collection: node data to subset.
    :param ids: unique ID(s) of node data to subset.
    :return: dataframe of node data subset for only the provided ``ids``.
    """
    if isinstance(ids, Hashable):
        ids = [ids]
    return node_collection.data.loc[
        node_collection.data[node_collection.unique_id_column].isin(ids), :
    ]
