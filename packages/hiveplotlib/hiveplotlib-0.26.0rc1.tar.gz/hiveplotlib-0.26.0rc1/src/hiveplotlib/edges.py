# edges.py
"""
``Edges`` instance and helper methods for edge construction.
"""

from copy import deepcopy
from typing import Hashable, Literal, Optional, Union

import numpy as np
import pandas as pd


class Edges:
    """
    Multi-edge aggregator with helper methods useful for downstream hive plots.

    An edge is specificed with respect to its starting node unique ID and ending node unique ID.

    The ``Edge`` class ingests an input ``pandas.DataFrame`` or ``(n, 2)`` ``numpy.ndarray`` (``data``) with
    specification for which data columns correspond to the starting node IDs (``from_column_name``) and ending node IDs
    (``to_column_name``).

    Users can also provide a dictionary of dataframes or arrays, where each key corresponds to a unique
    identifier for that set of edges. This allows users to store multiple sets of edges in a single ``Edges`` instance.

    By providing a ``pandas.DataFrame`` input, additional edge metadata can be provided for later use (e.g. subsetting
    edges by metadata, keyword arguments for plotting edges with different thickness / color, etc.).

    Users can thus visualize *groups* of edges in different ways in a single hive plot by providing a dictionary of
    dataframes with different edge metadata. Alternatively, users can provide a single
    ``pandas.DataFrame`` with all edges and vary plotting keyword arguments within metadata columns.

    Users can provide edge-plotting keyword arguments via the ``edge_viz_kwargs`` parameter in two ways.

    1. By providing a string value corresponding to a column name if a DataFrame is provided for edges, in which case
    that column data would be used for that plotting keyword argument in an ``edge_viz()`` call.

    2. By providing explicit keyword arguments (e.g. ``cmap="viridis"``), in which case that keyword argument would
    be used as-is in an ``edge_viz()`` call.

    ``edge_kwargs`` can also be updated (or overwritten) after instantiation via the
    :py:meth:`~hiveplotlib.Edges.update_edge_viz_kwargs()` method.

    :param data: data to store as edges. Can provide either a single ``pandas.DataFrame`` / 2d ``numpy.ndarray``, or a
        dictionary of dataframes / arrays, where each key corresponds to a unique identifier for that set of edges.
        If providing a ``numpy.ndarray``, then it should be of shape ``(n, 2)`` where the first column corresponds to
        the starting node IDs and the second column corresponds to the ending node IDs.
    :param from_column_name: name of the edge origin column, whose values correspond to node IDs where a given edge
        starts.
    :param to_column_name: name of the edge destination column, whose values correspond to node IDs where a given edge
        ends.
    :param edge_viz_kwargs: keyword arguments to provide to an ``edge_viz()`` call. Users can provide names according
        to column names in the ``data`` attribute or explicit values, as discussed in (1) and (2) above.

    .. note::
        If providing an array input for the ``data`` parameter, then it is required that the first column be the
        starting node IDs and the second column be the ending node IDs.

        Array inputs will be stored in the ``data`` attribute as a ``pandas.DataFrame`` with column names ``"from"`` and
        ``"to"``.

        Dictionary inputs for the ``data`` parameter can have any key, but the values must be either
        ``pandas.DataFrame`` or ``numpy.ndarray``. If a ``numpy.ndarray`` is provided, it must be of shape
        ``(n, 2)`` where the first column corresponds to the starting node IDs and the second column corresponds to the
        ending node IDs. If a ``pandas.DataFrame`` is provided, then it must have columns named according to the
        ``from_column_name`` and ``to_column_name`` parameters.

        Provided keyword argument values will be checked *first* against column names in
        ``Edges.data`` (i.e. (1) above) before falling back to (2) and setting the keyword argument
        explicitly.

        The appropriate keyword argument names should be chosen as a function of your choice of visualization back
        end (e.g. ``matplotlib``, ``bokeh``, ``datashader``, etc.).
    """

    def __repr__(self) -> str:
        """
        Make printable representation (repr) for ``Edges`` instance.
        """
        kws = list(self._data.keys())

        if len(kws) == 0:  # pragma: no cover
            return "hiveplotlib.Edges of 0 edges."

        if len(kws) == 1:
            return (
                f"hiveplotlib.Edges of {list(self._data.values())[0].shape[0]} edges."
            )

        sizes = [self._data[kw].shape[0] for kw in kws]
        return f"hiveplotlib.Edges of {sum(sizes)} edges across {len(kws)} tags."

    def __len__(self) -> int:
        """
        Allow ``len()`` to correspond to the number of nodes in the ``Edges`` over all tags.

        :return: number of edges (i.e. rows) in ``Edges.data``.
        """
        return sum([d.shape[0] for d in self._data.values()])

    def __init__(
        self,
        data: Union[
            pd.DataFrame, np.ndarray, dict[Hashable, Union[np.ndarray, pd.DataFrame]]
        ],
        from_column_name: Hashable = "from",
        to_column_name: Hashable = "to",
        edge_viz_kwargs: Optional[dict] = None,
    ) -> None:
        """Initialize."""
        # TODO: keep an `data_subset` attribute distinct from `data`. This will support plotting edge subsets
        # TODO: keep an `data_highlight` attribute distinct from `data`. This will support highlighting edges in plot

        self.from_column_name = from_column_name
        self.to_column_name = to_column_name

        self.edge_viz_kwargs = {} if edge_viz_kwargs is None else edge_viz_kwargs.copy()

        self._data = self._validate_edge_data(data)

        # nested dictionary that stores boolean 1d arrays of which edges are relevant to which set of edges plotted
        #  edges are plotted in chunks of "from axis", "to axis", and "tag", so this stores 1 boolean array nested in
        #  `relevant_edges[from_axis_id][to_axis_id][tag]`
        self.relevant_edges = {}

    def _validate_edge_data(
        self,
        data: Union[
            pd.DataFrame, np.ndarray, dict[Hashable, Union[np.ndarray, pd.DataFrame]]
        ],
    ) -> dict[Hashable, pd.DataFrame]:
        """
        Validate edge data and convert to a dictionary of ``pandas.DataFrame`` objects.

        :param data: edge data to validate. Can be a single ``pandas.DataFrame``, a ``numpy.ndarray``, or a dictionary
            of either.
        :return: dictionary of ``pandas.DataFrame`` objects with validated edge data.
        """
        if not isinstance(data, dict):
            if isinstance(data, np.ndarray):
                assert data.shape[1] == 2, (
                    "Any `numpy.ndarray` input in `data` must be shape (n, 2) "
                    f"but found input with {data.shape[1]} columns."
                )
                data = pd.DataFrame(
                    data, columns=[self.from_column_name, self.to_column_name]
                )
            data = {0: data}  # default to tag 0 for single dataframe provided
            if 0 not in self.edge_viz_kwargs:
                self.edge_viz_kwargs[0] = {}
        for kw in data:
            assert isinstance(data[kw], (pd.DataFrame, np.ndarray)), (
                f"Provided data for tag {kw} must be a `pandas.DataFrame` or `numpy.ndarray`."
            )
            if isinstance(data[kw], pd.DataFrame):
                assert self.from_column_name in data[kw].columns, (
                    f"Provided data for tag {kw} must have a column named '{self.from_column_name}'"
                )
                assert self.to_column_name in data[kw].columns, (
                    f"Provided data for tag {kw} must have a column named '{self.to_column_name}'"
                )
            elif isinstance(data[kw], np.ndarray):
                assert data[kw].shape[1] == 2, (
                    "Any `numpy.ndarray` input in `data` must be shape (n, 2) "
                    f"but found input with {data[kw].shape[1]} columns."
                )
                data[kw] = pd.DataFrame(
                    data[kw], columns=[self.from_column_name, self.to_column_name]
                )
            if kw not in self.edge_viz_kwargs:
                self.edge_viz_kwargs[kw] = {}
        return data

    @property
    def data(self) -> Union[pd.DataFrame, dict[Hashable, pd.DataFrame]]:
        """
        Getter for the ``Edges.data`` attribute.

        :return: when there is only a single tag of edges, returns the ``pandas.DataFrame`` of edges.
            When there are multiple tags of edges, returns a dictionary of ``pandas.DataFrame`` objects, where each key
            corresponds to the tag assigned for each set of edges.
        """
        if len(self._data) == 1:
            return list(self._data.values())[0]
        return self._data

    def add_edges(
        self,
        data: dict[Hashable, Union[np.ndarray, pd.DataFrame]],
    ) -> None:
        """
        Add edges to the ``Edges`` instance.

        .. note::
            If adding edge data with a tag matching an existing tag, then edge data to add must have the same from and
            to columns as the existing data with the same tag.

            2d arrays of data will always be accepted, but their edge data will be converted to ``pandas.DataFrame``.

        :param data: dictionary of data to add as edges. The key is a unique identifier to correspond to the added data
            value.
        :raises AssertionError: if the provided ``data`` includes an invalid shaped ``numpy.ndarray`` or if the
            provided ``data`` for a tag has different columns than the existing data for that tag.
        :return: ``None``.
        """
        cleaned_data = self._validate_edge_data(data)
        for kw in data:
            if kw not in self._data:
                self._data[kw] = cleaned_data[kw]
            else:
                self._data[kw] = pd.concat([self._data[kw], cleaned_data[kw]])

        return

    def copy(self) -> "Edges":
        """
        Return a copy of the ``Edges`` instance.

        :return: copy of the ``Edges`` instance.
        """
        return Edges(
            data=self._data.copy(),
            from_column_name=self.from_column_name,
            to_column_name=self.to_column_name,
            edge_viz_kwargs=deepcopy(self.edge_viz_kwargs),
        )

    def export_edge_array(
        self,
        tag: Union[Hashable, Literal["all"]] = "all",
    ) -> np.ndarray:
        """
        Return an ``(n, 2)`` array of [from, to] edges for the edge data corresponding to ``tag``.

        :param tag: tag of data to export. If ``all``, then all tags of edge data are exported as a single array.
        :raises AssertionError: if the provided ``tag`` is not a valid key in the ``Edges.data`` attribute.
        :return: array of [from, to] edges.
        """
        if tag == "all":
            return np.vstack(
                [
                    self._data[kw]
                    .loc[:, [self.from_column_name, self.to_column_name]]
                    .to_numpy()
                    for kw in self._data
                ]
            )
        assert tag in self._data, (
            f"Provided tag {tag} is not a valid key in the `Edges.data` attribute. "
            f"Valid keys are: {list(self._data.keys())}."
        )
        return (
            self._data[tag]
            .loc[:, [self.from_column_name, self.to_column_name]]
            .to_numpy()
        )

    def update_edge_viz_kwargs(
        self,
        tag: Optional[Hashable] = None,
        reset_kwargs: bool = False,
        **edge_viz_kwargs,
    ) -> None:
        """
        Update keyword arguments for plotting edges in a ``edge_viz()`` call.

        Users can either provide values in two ways.

        1. By providing a string value corresponding to a column name, in which case that column data would be used for
        that plotting keyword argument in a ``edge_viz()`` call.

        2. By providing explicit keyword arguments (e.g. ``cmap="viridis"``), in which case that keyword argument would
        be used as-is in a ``edge_viz()`` call.

        .. note::
            Provided keyword argument values will be checked *first* against column names in
            ``Edges.data`` (i.e. (1) above) before falling back to (2) and setting the keyword argument
            explicitly.

            The appropriate keyword argument names should be chosen as a function of your choice of visualization back
            end (e.g. ``matplotlib``, ``bokeh``, ``datashader``, etc.).

            These edge keyword arguments will be deprioritized in favor of any keyword arguments provided to any of the
            edge kwargs stored in the ``HivePlot.edge_plotting_keyword_arguments`` attribute.

        :param tag: tag of edge data to update keyword arguments for. If ``None``, then the keyword arguments are
            updated for all tags of edge data.
        :param reset_kwargs: whether to drop the existing keyword arguments before adding the provided keyword arguments
            to the ``edge_viz_kwargs`` attribute. Existing values are preserved by default (i.e.
            ``reset_kwargs=False``).
        :param edge_viz_kwargs: keyword arguments to provide to a ``edge_viz()`` call. Users can provide names according
            to column names in the ``data`` attribute or explicit values, as discussed in (1) and (2) above.
        :raises AssertionError: if the provided ``tag`` is not a valid key in the ``Edges.data`` attribute.
        :return: ``None``.
        """
        if tag is not None:
            assert tag in self._data, (
                f"Provided tag {tag} is not a valid key in the `Edges.data` attribute. "
                f"Valid keys are: {list(self._data.keys())}."
            )
            tags_to_use = [tag]
        else:
            tags_to_use = list(self._data.keys())
        for t in tags_to_use:
            if t not in self.edge_viz_kwargs:  # pragma: no cover
                self.edge_viz_kwargs[t] = {}
            if reset_kwargs:
                self.edge_viz_kwargs[t] = edge_viz_kwargs
            else:
                self.edge_viz_kwargs[t] |= edge_viz_kwargs
        return
