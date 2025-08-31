# converters.py

"""
Converters from various data structures to ``hiveplotlib``-ready structures.
"""

from typing import Tuple

import pandas as pd

from hiveplotlib import Edges, Node, NodeCollection
from hiveplotlib.node import node_collection_from_node_list

# say the graph type instead of calling `nx.Graph` to keep networkx dep out of this file.
NetworkXGraph = "networkx.classes.graph.Graph instance"


def networkx_to_nodes_edges(
    graph: NetworkXGraph,
    unique_id_name: str = "unique_id",
    check_uniqueness: bool = True,
) -> Tuple[NodeCollection, Edges]:  # type: ignore
    """
    Take a ``networkx`` graph and return ``hiveplotlib``-friendly data structures.

    Specifically, returns a ``NodeCollection`` instance of node data and an ``Edges`` instance of
    edge data. These outputs can be fed directly into :py:func:`~hiveplotlib.HivePlot`.

    :param graph: ``networkx`` graph.
    :param unique_id_name: name to use for unique IDs.
    :param check_uniqueness: whether or not to check that provided ``Node`` instances have unique IDs.
    :return: ``list`` of ``Node`` instances, ``(n, 2)`` ``np.ndarray`` of edges.
    """
    nodes = [Node(unique_id=i, data=data) for i, data in list(graph.nodes.data())]
    edge_keys = pd.DataFrame(list(graph.edges.keys()), columns=["from", "to"])
    edge_values = pd.DataFrame(list(graph.edges.values()))
    return node_collection_from_node_list(
        node_list=nodes,
        unique_id_name=unique_id_name,
        check_uniqueness=check_uniqueness,
    ), Edges(data=edge_keys.join(edge_values))
