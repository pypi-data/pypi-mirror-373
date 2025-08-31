# datasets.py

"""
Quick example datasets for use in ``hiveplotlib``.

For Hive Plots, many excellent network datasets are available online, including many graphs that can be generated using
`networkx <https://networkx.org/documentation/stable/reference/generators.html>`_ and
`pytorch-geometric <https://pytorch-geometric.readthedocs.io/en/latest/notes/data_cheatsheet.html#>`_.
The `Stanford Large Network Dataset Collection <https://snap.stanford.edu/data/>`_ is also a great general source of
network datasets. If working with ``networkx`` graphs,
users can also take advantage of the ``hiveplotlib.converters.networkx_to_nodes_edges()`` method to quickly get those
graphs into a ``hiveplotlib``-ready format.

For Polar Parallel Coordinates Plots (P2CPs), many datasets are available through packages including
`statsmodels <https://www.statsmodels.org/stable/datasets/index.html>`_ and
`scikit-learn <https://scikit-learn.org/stable/datasets.html>`_.
"""

from hiveplotlib.datasets.international_trade import *  # noqa: F401, F403
from hiveplotlib.datasets.toy_hive_plots import *  # noqa: F401, F403
from hiveplotlib.datasets.toy_p2cps import *  # noqa: F401, F403
