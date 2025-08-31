"""
Tools for generating toy hive plots.
"""

from typing import Dict, Hashable, List, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd

from hiveplotlib import (
    BaseHivePlot,
    Node,
    NodeCollection,
    hive_plot_n_axes,
)
from hiveplotlib.edges import Edges
from hiveplotlib.hiveplot import HivePlot
from hiveplotlib.node import dataframe_to_node_list


def example_base_hive_plot(
    num_nodes: int = 15,
    num_edges: int = 30,
    seed: int = 0,
    **hive_plot_n_axes_kwargs,
) -> BaseHivePlot:
    """
    Generate example hive plot with ``"Low"``, ``"Medium"``, and ``"High"`` axes (plus repeat axes).

    Nodes and edges will be generated and placed randomly.

    :param num_nodes: number of nodes to generate.
    :param num_edges: number of edges to generate.
    :param seed: random seed to use when generating nodes and edges.
    :param hive_plot_n_axes_kwargs: additional keyword arguments for the underlying
        :py:func:`hiveplotlib.hive_plot_n_axes()` call.
    :return: resulting ``BaseHivePlot`` instance.
    """
    color_dict = {
        "Low": {"Low_repeat": "#006BA4", "High_repeat": "#FF800E"},
        "High": {"Medium_repeat": "#ABABAB", "High_repeat": "#595959"},
        "Medium": {"Medium_repeat": "#5F9ED1", "Low_repeat": "#C85200"},
        "Low_repeat": {"Low": "#006BA4", "Medium": "#C85200"},
        "Medium_repeat": {"Medium": "#5F9ED1", "High": "#ABABAB"},
        "High_repeat": {"High": "#595959", "Low": "#FF800E"},
    }

    rng = np.random.default_rng(seed)
    data = pd.DataFrame(
        np.c_[
            rng.uniform(low=0, high=10, size=num_nodes),
            rng.uniform(low=10, high=20, size=num_nodes),
            rng.uniform(low=20, high=30, size=num_nodes),
        ],
        columns=["low", "med", "high"],
    )

    # make indices a column
    data = data.reset_index(names="unique_id")

    edges = rng.choice(data["unique_id"].to_numpy(), size=num_edges * 2).reshape(-1, 2)

    hp = hive_plot_n_axes(
        nodes=NodeCollection(data=data, unique_id_column="unique_id"),
        edges=edges,
        axes_assignments=[
            np.arange(num_nodes)[: num_nodes // 3],
            np.arange(num_nodes)[num_nodes // 3 : 2 * num_nodes // 3],
            np.arange(num_nodes)[2 * num_nodes // 3 :],
        ],
        sorting_variables=["low", "med", "high"],
        repeat_axes=[True, True, True],
        axes_names=["Low", "Medium", "High"],
        orient_angle=-30,
        **hive_plot_n_axes_kwargs,
    )

    # set colors according to above-defined color dictionary
    #  (so we can replicate more easily in other viz later)
    for e1 in color_dict:
        for e2 in color_dict[e1]:
            hp.add_edge_kwargs(axis_id_1=e1, axis_id_2=e2, color=color_dict[e1][e2])

    return hp


def example_node_data(num_nodes: int = 100, seed: int = 0) -> pd.DataFrame:
    """
    Generate example node dataframe.

    Each node will have a ``"low"``, ``"med"``, and ``"high"`` value, where these values are randomly generated, and as
    the names suggest, for the resulting values of each node, ``"low"`` < ``"med"`` < ``"high"``.

    Unique ID column will be given the name ``"unique_id"``.

    :param num_nodes: how many nodes to randomly generate. Node unique IDs will be the integers 0, 1, ... ,
        ``num_nodes - 1``.
    :param seed: random seed to use when randomly generating node data.
    :return: dataframe of node data.
    """
    rng = np.random.default_rng(seed)
    # example data
    data = pd.DataFrame(
        np.c_[
            rng.uniform(low=0, high=9.99, size=num_nodes),
            rng.uniform(low=10, high=19.99, size=num_nodes),
            rng.uniform(low=20, high=29.99, size=num_nodes),
        ],
        columns=["low", "med", "high"],
    )
    # make indices a column
    return data.reset_index(names="unique_id")


def example_node_collection(
    num_nodes: int = 100,
    seed: int = 0,
    unique_id_column: str = "unique_id",
) -> NodeCollection:
    """
    Generate example ``NodeCollection``.

    Each node will have a ``"low"``, ``"med"``, and ``"high"`` value, where these values are randomly generated, and as
    the names suggest, for the resulting values of each node, ``"low"`` < ``"med"`` < ``"high"``.

    Unique ID column will be given the name ``"unique_id"``.

    :param num_nodes: how many nodes to randomly generate. Node unique IDs will be the integers 0, 1, ... ,
        ``num_nodes - 1``.
    :param seed: random seed to use when randomly generating node data.
    :param unique_id_column: name to assign to the column in the resulting ``NodeCollection.data`` attribute that
        corresponds to the unique IDs.
    :return: ``NodeCollection`` of node data.
    """
    data = example_node_data(num_nodes=num_nodes, seed=seed)
    data = data.rename(columns={"unique_id": unique_id_column})
    return NodeCollection(
        data=data,
        unique_id_column=unique_id_column,
    )


def example_edge_data(
    nodes: NodeCollection,
    num_edges: int = 100,
    from_column_name: Hashable = "from",
    to_column_name: Hashable = "to",
    seed: int = 0,
) -> pd.DataFrame:
    """
    Generate example edge data from a provided ``NodeCollection``.

    :param nodes: nodes from which to generate example edges.
    :param num_edges: how many example edges to randomly generate.
    :param from_column_name: name to assign to the edge origin column, whose values correspond to node IDs where a given
        edge starts.
    :param to_column_name: name to assign to the edge destination column, whose values correspond to node IDs where a
        given edge ends.
    :param seed: random seed to use when randomly generating edge data.
    :return: random edge data as (n, 2) DataFrame of [from, to] edges.
    """
    node_ids = nodes.data[nodes.unique_id_column].to_numpy()
    rng = np.random.default_rng(seed)
    edge_array = rng.choice(node_ids, size=num_edges * 2).reshape(-1, 2)
    return pd.DataFrame(edge_array, columns=[from_column_name, to_column_name])


def example_edges(
    nodes: NodeCollection,
    num_edges: int = 100,
    from_column_name: Hashable = "from",
    to_column_name: Hashable = "to",
    seed: int = 0,
) -> Edges:
    """
    Generate example edges from a provided ``NodeCollection``.

    :param nodes: nodes from which to generate example edges.
    :param num_edges: how many example edges to randomly generate.
    :param from_column_name: name to assign to the edge origin column, whose values correspond to node IDs where a given
        edge starts.
    :param to_column_name: name to assign to the edge destination column, whose values correspond to node IDs where a
        given edge ends.
    :param seed: random seed to use when randomly generating edge data.
    :return: random edge data.
    """
    edge_df = example_edge_data(
        nodes=nodes,
        num_edges=num_edges,
        from_column_name=from_column_name,
        to_column_name=to_column_name,
        seed=seed,
    )

    return Edges(
        data=edge_df,
        from_column_name=from_column_name,
        to_column_name=to_column_name,
    )


def example_nodes_and_edges(
    num_nodes: int = 100,
    num_edges: int = 200,
    num_axes: int = 3,
    seed: int = 0,
) -> Tuple[List[Node], List[List[Hashable]], np.ndarray]:
    """
    Generate example nodes, node splits (one list of nodes per intended axis), and edges.

    Each node will have a ``"low"``, ``"med"``, and ``"high"`` value, where these values are randomly generated, and as
    the names suggest, for the resulting values of each node, ``"low"`` < ``"med"`` < ``"high"``.

    :param num_nodes: how many nodes to randomly generate. Node unique IDs will be the integers 0, 1, ... ,
        ``num_nodes - 1``.
    :param num_edges: how many edges to randomly generate.
    :param num_axes: how many axes into which to partition the randomly generated nodes.
    :param seed: random seed to use when randomly generating node and edge data.
    :return: list of generated ``Node`` instances, a list of ``num_axes`` lists that evenly split the node IDs to be
        allocated to their own axes, and a ``(num_edges, 2)`` shaped array of random edges between nodes.
    """
    data = example_node_data(num_nodes=num_nodes, seed=seed)
    node_list = dataframe_to_node_list(data, unique_id_column="unique_id")
    node_ids = data["unique_id"].to_numpy()

    # split node allocation equally among planned axes
    node_ids_per_axis = np.split(node_ids, num_axes)
    # coax to list of lists
    node_ids_per_axis = [i.tolist() for i in node_ids_per_axis]

    rng = np.random.default_rng(seed)
    edges = rng.choice(node_ids, size=num_edges * 2).reshape(-1, 2)

    return node_list, node_ids_per_axis, edges


def example_hive_plot(
    num_nodes: int = 100,
    num_edges: int = 100,
    partition_data_column: Literal["low", "med", "high"] = "low",
    labels: Optional[List[Hashable]] = ("A", "B", "C"),
    cutoffs: Optional[Union[List[float], int]] = 3,
    partition_variable_name: Optional[Hashable] = None,
    sorting_variables: Union[Hashable, Dict[Hashable, Hashable]] = "low",
    seed: int = 0,
    node_unique_id_column: str = "unique_id",
    **hive_plot_kwargs,
) -> HivePlot:
    """
    Generate example ``HivePlot`` instance.

    Each node will have a ``"low"``, ``"med"``, and ``"high"`` value, where these values are randomly generated, and as
    the names suggest, for the resulting values of each node, ``"low"`` < ``"med"`` < ``"high"``.

    Each edge will also have a ``"low"``, ``"med"``, and ``"high"`` value, with each value being the average "low" /
    "med" / "high" level of the two nodes composing the edge.

    .. note::
        The generated ``num_edges`` edges will be randomly generated between *all possible axes, including repeat axes*.
        Thus, calling this function without requesting *all* repeat axes (i.e. ``repeat_axes=True``) will result in less
        than ``num_edges`` edges visualized in the final hive plot. (All generated edges will be stored in the resulting
        ``hive_plot.edges``, even though some will not be plotted if excluding repeat axes in the plot.)

    :param num_nodes: how many nodes to randomly generate. Node unique IDs will be the integers 0, 1, ... ,
        ``num_nodes - 1``.
    :param num_edges: how many example edges to randomly generate.
    :param partition_data_column: which column of data in the underlying ``data`` attribute to use to partition the
        node data. Node data generated via :py:func:`hiveplotlib.datasets.toy_hive_plots.example_node_data()`.
    :param labels: labels assigned to each bin. Only referenced when ``cutoffs`` is not ``None``. ``None``
        labels each bin as a string based on its range of values. Note, when ``cutoffs`` is a list, ``len(labels)``
        must be 1 greater than ``len(cutoffs)``. When ``cutoffs`` is an ``int``, ``len(labels)`` must be equal to
        ``cutoffs``.
    :param cutoffs: cutoffs to use in binning nodes according to data under ``partition_data_column``. Default ``None``
        will bin nodes by unique values of ``partition_data_column``. When provided as a ``list``, the specified cutoffs
        will bin according to (-inf, ``cutoffs[0]``], (``cutoffs[0]``, ``cutoffs[1]``], ... , (``cutoffs[-1]``, inf).
        When provided as an ``int``, the exact numerical break points will be determined to create ``cutoffs``
        equally-sized quantiles.
    :param partition_variable_name: name of the resulting partition variable to add to the ``nodes.data`` attribute of
        the resulting ``HivePlot`` instance. Default ``None`` will name the partition column as ``"partition_0"``.
    :param sorting_variable: which node variable to use to sort / place the nodes on each axis. Providing a single
        value uses the same variable for each axis. Alternatively, providing a dictionary of keys as the unique values
        from ``partition_variable_name`` column data in the ``nodes.data`` attribute and values being the corresponding
        sorting variable to use for that axis.
    :param seed: random seed to use when randomly generating node and edge data.
    :param node_unique_id_column: name to assign to the column in the ``nodes.data`` attribute that corresponds to the
        unique IDs.
    :param hive_plot_kwargs: additional keyword arguments when creating the returned
        :py:class:`hiveplotlib.HivePlot()` instance.
    :return: randomly-generated ``HivePlot`` instance.
    """
    node_collection = example_node_collection(
        num_nodes=num_nodes,
        seed=seed,
        unique_id_column=node_unique_id_column,
    )
    edges = example_edges(
        nodes=node_collection,
        num_edges=num_edges,
        seed=seed,
    )

    temp_df = (
        edges._data[0]
        .merge(
            node_collection.data,
            left_on="from",
            right_on=node_unique_id_column,
        )
        .merge(
            node_collection.data,
            left_on="to",
            right_on=node_unique_id_column,
            suffixes=[None, "_to"],
        )
    )
    for col in ["low", "med", "high"]:
        edges._data[0][col] = (temp_df[col] + temp_df[f"{col}_to"]) / 2

    partition_variable = node_collection.create_partition_variable(
        data_column=partition_data_column,
        cutoffs=cutoffs,
        labels=labels,
        partition_variable_name=partition_variable_name,
    )
    return HivePlot(
        nodes=node_collection,
        edges=edges,
        partition_variable=partition_variable,
        sorting_variables=sorting_variables,
        **hive_plot_kwargs,
    )
