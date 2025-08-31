# viz.py

"""
Viz functions to be called on ``hiveplotlib.HivePlot``, ``hiveplotlib.BaseHivePlot``, or ``hiveplotlib.P2CP`` instances.

Default visualization functions exposed in ``hiveplotlib.viz`` use ``matplotlib``, but additional viz backends are
supported in additional submodules of ``hiveplotlib.viz``.
"""

from hiveplotlib.viz.matplotlib import (  # noqa: F401
    axes_viz,
    edge_viz,
    hive_plot_viz,
    label_axes,
    node_viz,
    p2cp_legend,
    p2cp_viz,
)
