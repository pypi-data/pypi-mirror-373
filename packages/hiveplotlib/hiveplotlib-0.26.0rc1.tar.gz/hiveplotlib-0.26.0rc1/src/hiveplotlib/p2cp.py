# p2cp.py

"""
Definition of ``P2CP`` instance and helper static methods for generating and working with ``P2CP`` instances.
"""

import json
import warnings
from copy import deepcopy
from typing import Dict, Hashable, List, Literal, Optional, Union

import numpy as np
import pandas as pd

from hiveplotlib.axis import Axis
from hiveplotlib.hiveplot import BaseHivePlot
from hiveplotlib.node import NodeCollection


class P2CP:
    """
    Polar Parallel Coordinates Plots (P2CPs).

    Conceptually similar to Hive Plots, P2CPs can be used for any multivariate
    data as opposed to solely for network visualizations. Features of the data are placed on their own axes in the same
    polar setup as Hive Plots, resulting in each representation of a complete data point being a *loop* in the resulting
    figure. For more on the nuances of P2CPs, see `Koplik and Valente, 2021 <https://arxiv.org/abs/2109.10193>`_.
    """

    def __init__(self, data: Optional[pd.DataFrame] = None) -> None:
        """
        Initialize P2CP instance.
        """
        # backend ``Node`` instances (NodeCollection)
        self._node_collection = None

        # track the data the user has added
        if data is not None:
            self.set_data(data=data)
        else:
            self.data = None

        # track what axes the user has chosen along with specified vmin and vmax values
        # (e.g. each `self.axes['column_id']` has keys "axis", "vmin", and "vmax")
        self.axes = {}

        # also track a list, from which will connect the ith to the i+1st axes (plus the last to the first)
        self.axes_list = []

        # backend ``BaseHivePlot`` instance
        self._hiveplot = BaseHivePlot()

        # track tags
        self.tags = []

    def __build_underlying_node_collection(self) -> None:
        """
        Build underlying ``NodeCollection`` instance which will become the loops in the eventual P2CP to be visualized.

        .. note::
            This is a hidden method because everything relating to the underlying `BaseHivePlot` instance is
            unnecessary / unintuitive to the user generating P2CPs.

        :return: ``None``.
        """
        node_data = self.data.reset_index(names="unique_id")
        self._node_collection = NodeCollection(
            data=node_data, unique_id_column="unique_id"
        )

    def set_data(self, data: pd.DataFrame) -> None:
        """
        Add a dataset to the ``P2CP`` instance.

        All P2CP construction will be based on this dataset, which will be stored as ``P2CP.data``.

        :param data: dataframe to add.
        :return: ``None``.
        """
        assert isinstance(data, pd.DataFrame), "`data` must be pandas DataFrame."

        self.data = data

        # also build the ``NodeCollection`` instance we'll need for underlying ``HivePlot`` calls later
        self.__build_underlying_node_collection()

    def __build_underlying_hiveplot_instance(self) -> None:
        """
        Build the underlying ``BaseHivePlot`` instance which will become the eventual P2CP to be visualized.

        .. note::
            This is a hidden method because everything relating to the underlying `BaseHivePlot` instance is
            unnecessary / unintuitive to the user generating P2CPs.

        :return: ``None``.
        """
        hp = BaseHivePlot()
        hp.add_nodes(self._node_collection)
        axes = [self.axes[k]["axis"] for k in self.axes]
        hp.add_axes(axes)
        for axis_id in hp.axes:
            # make sure to *sort* on axes without any "\nrepeat" in there for the repeat axes' names
            sorting_variable = axis_id.split("\nRepeat")[0]
            # put *all* the nodes on each axis
            hp.place_nodes_on_axis(
                axis_id=axis_id,
                node_df=hp.nodes.data,
                sorting_feature_to_use=sorting_variable,
                vmin=self.axes[axis_id]["vmin"],
                vmax=self.axes[axis_id]["vmax"],
            )
        self._hiveplot = hp

    def set_axes(
        self,
        columns: Union[List[Hashable], np.ndarray],
        angles: Optional[List[float]] = None,
        vmins: Optional[List[float]] = None,
        vmaxes: Optional[List[float]] = None,
        axis_kwargs: Optional[List[Dict]] = None,
        overwrite_previously_set_axes: bool = True,
        start_angle: float = 0,
    ) -> None:
        r"""
        Set the axes that will be used in the eventual P2CP visualization.

        :param columns: column names from ``P2CP.data`` to use. Note, these need not be unique, as repeat axes may be
            desired. By default, repeat column names will be internally renamed to name + ``"\nRepeat"``.
        :param angles: corresponding angles (in degrees) to set for each desired axis. Default ``None`` sets the angles
            evenly spaced over 360 degrees, starting at ``start_angle`` degrees for the first axis and moving
            counterclockwise.
        :param vmins: list of ``float`` values (or ``None`` values) specifying the vmin for each axis, where the ith
            index value corresponds to the ith axis set by ``columns``. A ``None`` value infers the global min for that
            axis. Default ``None`` uses the global min for all axes.
        :param vmaxes: list of ``float`` values (or ``None`` values) specifying the vmax for each axis, where the ith
            index value corresponds to the ith axis set by ``columns``. A ``None`` value infers the global max for that
            axis. Default ``None`` uses the global max for all axes.
        :param axis_kwargs: list of dictionaries of additional kwargs that will be used for the underlying ``Axis``
            instances that will be created for each column. Only relevant if you want to change the positioning / length
            of an axis with the ``start`` and ``end`` parameters. For more on these kwargs, see the documentation for
            ``hiveplotlib.Axis``. Note, if you want to add these kwargs for only a subset of the desired axes, you can
            skip adding kwargs for specific columns by putting a ``None`` at those indices in your ``axis_kwargs``
            input.
        :param overwrite_previously_set_axes: Whether to overwrite any previously decided axes. Default ``True``
            overwrites any existing axes.
        :param start_angle: if ``angles`` is ``None``, sets the starting angle from which we place the axes around the
            origin counterclockwise.
        :return: ``None``.
        """
        num_columns = np.array(columns).size

        for c in columns:
            assert c in self.data.columns, (
                f"Column {c} not in `P2CP.data`, cannot set axis as non-existent variable."
            )

        if angles is not None:
            assert num_columns == np.array(angles).size, (
                "`columns` and `angles` not the same size."
            )
        # build out evenly-spaced `angles` if not provided
        else:
            spacing = 360 / num_columns
            angles = np.arange(
                start_angle, start_angle + num_columns * spacing, spacing
            )
            # make sure we're still in [0, 360)
            angles = np.mod(angles, 360)

        if vmins is None:
            vmins = [None] * num_columns
        else:
            assert np.array(vmins).size == num_columns, (
                "`vmins` and `columns` not the same size."
            )

        if vmaxes is None:
            vmaxes = [None] * num_columns
        else:
            assert np.array(vmaxes).size == num_columns, (
                "`vmaxes` and `columns` not the same size."
            )

        if axis_kwargs is None:
            axis_kwargs = [{}] * num_columns
        else:
            assert np.array(axis_kwargs).size == num_columns, (
                "`axis_kwargs` and `columns` not the same size."
            )
            # turn any `None values to empty dicts
            for i, kw in enumerate(axis_kwargs):
                if kw is None:
                    axis_kwargs[i] = {}

        # overwrite previously set axes
        if overwrite_previously_set_axes:
            self.axes = {}
            self.axes_list = []

        for c, a, kw, vmin, vmax in zip(
            columns,
            angles,
            axis_kwargs,
            vmins,
            vmaxes,
        ):
            if c in self.axes:
                c += "\nRepeat"
            self.axes[c] = {}
            self.axes[c]["axis"] = Axis(axis_id=c, angle=a, **kw)
            self.axes[c]["vmin"] = vmin
            self.axes[c]["vmax"] = vmax

            self.axes_list.append(c)

        # rebuild the underlying ``BaseHivePlot`` instance
        self.__build_underlying_hiveplot_instance()

        # all edges get scrapped, so no tags remain
        self.tags = []

    def build_edges(
        self,
        indices: Union[List[int], np.ndarray, Literal["all"]] = "all",
        tag: Optional[Hashable] = None,
        num_steps: int = 100,
        **edge_kwargs,
    ) -> Hashable:
        """
        Construct the loops of the P2CP for the specified subset of ``indices``.

        These index values correspond to the indices of the ``pandas`` dataframe ``P2CP.data``.

        .. note::
            Specifying ``indices="all"`` draws the curves for the entire dataframe.

        :param indices: which indices of the underlying dataframe to draw on the P2CP. Note, "all" draws the entire
            dataframe.
        :param tag: tag corresponding to specified indices. If ``None`` is provided, the tag will be set as the lowest
            unused integer starting at 0 amongst the tags.
        :param num_steps: number of points sampled along a given Bézier curve. Larger numbers will result in smoother
            curves when plotting later, but slower rendering.
        :param edge_kwargs: additional ``matplotlib`` keyword arguments that will be applied to edges constructed for
            the referenced indices.
        :return: the unique, ``Hashable`` tag used for the constructed edges.
        """
        # "edges" in P2CPs in the network context are to oneself
        if isinstance(indices, str) and indices == "all":
            ids = self._node_collection.data[
                self._node_collection.unique_id_column
            ].to_numpy()
        else:
            ids = indices

        if tag is None:
            # only need to find a unique tag if we've created edges already
            if len(list(self._hiveplot.hive_plot_edges.keys())) > 0:
                # same tags generated over all axes with P2CPs, just need to check over any pair
                tag = self._hiveplot._find_unique_tag(
                    from_axis_id=self.axes_list[0], to_axis_id=self.axes_list[1]
                )
            else:
                tag = 0
        edges = np.c_[ids, ids]
        for i, _ in enumerate(self.axes_list):
            first_axis = i
            second_axis = (i + 1) % len(self.axes_list)
            self._hiveplot.connect_axes(
                edges=edges,
                tag=tag,
                axis_id_1=self.axes_list[first_axis],
                axis_id_2=self.axes_list[second_axis],
                a2_to_a1=False,
                num_steps=num_steps,
                warn_on_no_edges=False,
                **edge_kwargs,
            )
        self.tags.append(tag)

        return tag

    def add_edge_kwargs(self, tag: Optional[Hashable] = None, **edge_kwargs) -> None:
        """
        Add edge kwargs to a tag of Bézier curves previously constructed with ``P2CP.build_edges()``.

        For a given tag of curves for which edge kwargs were already set, any redundant edge kwargs specified by this
        method call will overwrite the previously set kwargs.

        .. note::
            Expected to have previously called ``P2CP.build_edges()`` before calling this method, for the tag of
            interest. However, if no tags were ever set (e.g. there's only 1 tag of curves), then no tag is necessary
            here.

        :param tag: which subset of curves to modify kwargs for. Note, if no tag is specified (e.g. ``tag=None``), it is
            presumed there is only one tag to look over and that will be inferred. If no tag is specified and there are
            multiple tags to choose from, a ``ValueError`` will be raised.
        :param edge_kwargs: additional ``matplotlib`` keyword arguments that will be applied to edges constructed for
            the referenced indices.
        :return: ``None``.
        """
        if tag is None:
            assert len(self.tags) == 1, (
                f"No `tag` specified but multiple tags exist for this `P2CP` instance ({self.tags}). Cannot infer "
                "which tag to modify, please specify one of the tags with the `tag` parameter."
            )
            tag = self.tags[0]

        else:
            assert tag in self.tags, (
                "`tag` not in previously-generated tags, be sure to construct edges with `P2CP.build_edges()` first."
            )

        for i, _ in enumerate(self.axes_list):
            first_axis = i
            second_axis = (i + 1) % len(self.axes_list)
            self._hiveplot.add_edge_kwargs(
                axis_id_1=self.axes_list[first_axis],
                axis_id_2=self.axes_list[second_axis],
                tag=tag,
                a2_to_a1=False,
                **edge_kwargs,
            )

    def reset_edges(self, tag: Optional[Hashable] = None) -> None:
        """
        Drop the constructed edges with the specified ``tag``.

        .. note::
            If no tags were ever set (e.g. there's
            only 1 tag of curves), then no tag is necessary here.

        :param tag: which subset of curves to delete. Note, if no tag is specified (e.g. ``tag=None``), then all curves
            will be deleted.
        :return: ``None``.
        """
        if tag is None:
            self._hiveplot.reset_edges()

        else:
            for i, _ in enumerate(self.axes_list):
                first_axis = i
                second_axis = (i + 1) % len(self.axes_list)
                self._hiveplot.reset_edges(
                    axis_id_1=self.axes_list[first_axis],
                    axis_id_2=self.axes_list[second_axis],
                    tag=tag,
                    a2_to_a1=False,
                )

    def copy(self) -> "P2CP":
        """
        Return a copy of the ``P2CP`` instance.

        :return: ``P2CP`` instance.
        """
        return deepcopy(self)

    def to_json(self) -> str:
        """
        Return the information from the axes, point placement on each axis, and edges in Cartesian space as JSON.

        This allows users to visualize P2CPs with arbitrary libraries, even outside of python.

        The dictionary structure of the resulting JSON will consist of two top-level keys:

        "axes" - contains the information for plotting each axis, plus the points on each axis in Cartesian space.

        "edges" - contains the information for plotting the discretized edges in Cartesian space broken up by tag
        values, plus the corresponding unique IDs of points that go with each tag, as well as any kwargs that were set
        for plotting each set of points in a given tag.

        :return: JSON output of axis, point, and edge information.
        """
        # axis endpoints and node placements (both in Cartesian space).
        axis_node_dict = {}

        for axis in self._hiveplot.axes:
            # endpoints of axis in Cartesian space
            start, end = self._hiveplot.axes[axis].start, self._hiveplot.axes[axis].end

            temp_dict = {
                "start": start,
                "end": end,
                "points": self._hiveplot.axes[axis]
                .node_placements.loc[:, ["unique_id", "x", "y"]]
                .to_dict(orient="list"),
            }
            axis_node_dict[axis] = temp_dict

        edge_info = deepcopy(self._hiveplot.hive_plot_edges)

        # edge ids, discretized curves (in Cartesian space), and kwargs
        new_dict = {}
        # want to loop over the nested tags, not the axes like with hive plots
        #  (since every point in a tag is a complete loop)
        #  so let's just grab the first axis pair we can find and grab those tags, then loop over the tags instead
        temp_first_axis = list(edge_info.keys())[0]
        temp_second_axis = list(edge_info[temp_first_axis].keys())[0]

        for tag in edge_info[temp_first_axis][temp_second_axis]:
            new_dict[tag] = {}
            # ids and edge kwargs will be the same on every axis by construction of the P2CP
            # ids map to themselves in hive plot backend, so let's just store a single id for each
            new_dict[tag]["ids"] = [
                j[0]
                for j in edge_info[temp_first_axis][temp_second_axis][tag][
                    "ids"
                ].tolist()
            ]
            new_dict[tag]["edge_kwargs"] = edge_info[temp_first_axis][temp_second_axis][
                tag
            ]["edge_kwargs"]
            new_dict[tag]["curves"] = {}
            for a0 in edge_info:
                new_dict[tag]["curves"][a0] = {}
                for a1 in edge_info[a0]:
                    new_dict[tag]["curves"][a0][a1] = {}
                    # curves have nan values, must revise to `None` then coax to list
                    arr = edge_info[a0][a1][tag]["curves"]
                    temp = arr.astype("O")
                    temp[np.where(np.isnan(arr))] = None
                    new_dict[tag]["curves"][a0][a1] = temp.tolist()

        collated_output = {"axes": axis_node_dict, "edges": new_dict}

        return json.dumps(collated_output)


def p2cp_n_axes(
    data: pd.DataFrame,
    indices: Union[List[int], List[List[int]], List[np.ndarray], str] = "all",
    split_on: Optional[Union[Hashable, List[Hashable]]] = None,
    axes: Optional[List[Hashable]] = None,
    vmins: Optional[List[float]] = None,
    vmaxes: Optional[List[float]] = None,
    orient_angle: float = 0,
    all_edge_kwargs: Optional[Dict] = None,
    indices_list_kwargs: Optional[List[Dict]] = None,
) -> P2CP:
    """
    Generate a ``P2CP`` instance with an arbitrary number of axes for an arbitrary dataframe.

    Can specify a desired subset of column names, each of which will become an axis in the resulting P2CP.
    Default grabs all columns in the dataframe, unless ``split_on`` is a column name, in which case that specified
    column will be excluded from the list of axes in the final ``P2CP`` instance. Note, repeat axes (e.g. repeated
    column names) are allowed here.

    Axes will be added in counterclockwise order. Axes will all be the same length and position from the origin.

    In deciding what edges of ``data`` get drawn (and how they get drawn), the user has several options. The default
    behavior plots all data points in ``data`` with the same keyword arguments. If one instead wanted to plot a subset
    of data points, one can provide a ``list`` of a subset of indices from the dataframe to the ``indices`` parameter.

    If one wants to plot multiple *sets* of edges in different styles, there are two means of doing this. The more
    automated means is to split on the unique values of a column in the provided ``data``. By specifying
    a column name to the ``split_on`` parameter, data will be added in chunks according to the unique values of the
    specified column. If one instead includes a list of values corresponding to the records in ``data``, data will
    be added according to the unique values of this provided list.
    Each subset of ``data`` corresponding to a unique column value will be given a separate tag, with the
    tag being the unique column value. Note, however, this only works when ``indices="all"``. If one prefers to split
    indices manually, one can instead provide a list of lists to the ``indices`` parameter, allowing for arbitrary
    splitting of the data. Regardless of how one chooses to split the data, one can then assign different keyword
    arguments to each subset of data.

    Changes to all the edge kwargs can be affected with the ``all_edge_kwargs`` parameter. If providing multiple sets
    of edges though in one of the ways discussed above, one can also provide unique kwargs for each set
    of edges by specifying a corresponding ``list`` of dictionaries of kwargs with the ``indices_list_kwargs``
    parameter.

    Specific edge kwargs can also be changed later by running the ``add_edge_kwargs()`` method on the returned ``P2CP``
    instance. If one only added a single set of indices (e.g. ``indices="all"`` or ``indices`` was provided as a flat
    list of index values), then this method can simply be called with kwargs. However, if multiple subsets of edges were
    specified, then one will need to be precise about which ``tag`` of edge kwargs to change. If multiple sets were
    provided via the ``indices`` parameter, then the resulting ``tag`` for each subset will correspond to the index
    value in the list of lists in ``indices``. If instead ``split_on_column`` was specified as not ``None``, then tags
    will be the unique values in the specified column / list of values. Regardless of splitting methodology, existing
    tags can be found under the returned ``P2CP.tags``.

    There is a hierarchy to these kwarg arguments. That is, if redundant / overlapping kwargs are provided for
    different kwarg parameters, a warning will be raised and priority will be given according to the below hierarchy:

    ``indices_list_kwargs`` > ``all_edge_kwargs``.

    :param data: dataframe to add.
    :param indices: ``list`` of index values from the index of the added dataframe ``data``. Default "all" creates edges
        for every row in ``data``, but a ``list`` input creates edges for only the specified subset. Alternatively,
        one can provide a *list of lists* of indices, which will allow for plotting different sets of edges with
        different kwargs. These subsets will be added to the resulting ``P2CP`` instance with tags corresponding to
        the index value in ``indices``.
    :param split_on: column name from ``data`` or list of values corresponding to the records of ``data``.
        If specified as not ``None``, the resulting ``P2CP`` instance will split data according to unique values with
        respect to the column of ``data`` / the list of provided values, with each subset of data given a tag of the
        unique value corresponding to each subset. When specifying a column in ``data``, this column will be excluded
        from consideration if ``axes`` is ``None``. Note: this subsetting can only be run when ``indices="all"``.
        Default ``None`` plots all the records in ``data`` with the same line kwargs.
    :param axes: list of ``Hashable`` column names in ``data``. Each column name will be assigned to a separate axis in
        the resulting ``P2CP`` instance, built out in counterclockwise order. Default ``None`` grabs all columns in the
        dataframe, unless ``split_on`` is a column name, in which case that specified column will be excluded from
        the list of axes in the final ``P2CP`` instance. Note, repeat axes (e.g. repeated column names) are allowed
        here.
    :param vmins: list of ``float`` values (or ``None`` values) specifying the vmin for each axis, where the ith index
        value corresponds to the ith index axis in ``axes`` (e.g. the ith axis of the resulting ``P2CP``
        instance). A ``None`` value infers the global min for that axis. Default ``None`` uses the global min for
        all the axes.
    :param vmaxes: list of ``float`` values (or ``None`` values) specifying the vmax for each axis, where the ith index
        value corresponds to the ith index axis in ``axes`` (e.g. the ith axis of the resulting ``P2CP``
        instance). A ``None`` value infers the global max for that axis. Default ``None`` uses the global max for
        all the axes.
    :param orient_angle: rotates all axes counterclockwise from their initial angles (default 0 degrees).
    :param all_edge_kwargs: kwargs for all edges. Default ``None`` specifies no additional kwargs.
    :param indices_list_kwargs: list of dictionaries of kwargs for each element of ``indices`` when ``indices`` is a
        list of lists or ``split_on`` is not ``None``. The ith set of kwargs in ``indices_list_kwargs`` will only
        be applied to index values corresponding to the ith list in ``indices`` or to index values which have the ith
        unique value in a sorted list of unique values in ``split_on``. Default ``None`` provides no additional
        kwargs. Note, this list must be same length as ``indices`` or the same number of values as the number of unique
        values in ``split_on``.
    :return: ``P2CP`` instance.
    """
    # make sure kwarg arguments are correct
    if all_edge_kwargs is None:
        all_edge_kwargs = {}

    # default assumption, we are not splitting on a column unless explicitly ruled in later
    split_on_column = False

    # check if we have list of lists input
    #  if every element is size one, it's just a list of indices
    if indices == "all":
        if split_on is not None:
            if isinstance(split_on, (list, np.ndarray)):
                assert len(split_on) == data.shape[0], (
                    "If `split_on` is list-like, must have the same number of values as records in `data`"
                )
                tags = sorted(np.unique(split_on))
                indices = [list(np.where(split_on == t)[0]) for t in tags]
            else:
                split_on_column = True
                split_dict = indices_for_unique_values(df=data, column=split_on)
                tags = list(split_dict.keys())
                tags.sort()
                indices = [list(split_dict[t]) for t in tags]
            if indices_list_kwargs is None:
                indices_list_kwargs = [{} for _ in tags]
            else:
                assert len(indices) == len(indices_list_kwargs), (
                    "Must provide same number of sets of edges "
                    f"(currently unique splits specified by `split_on`={split_on} is "
                    f"{len(indices)}) as edge kwargs"
                    f"(currently len(indices_list_kwargs) = {len(indices_list_kwargs)}"
                )
        else:
            tags = [None]
            indices = [data.index.to_numpy()]
            if indices_list_kwargs is None:
                indices_list_kwargs = [{}]
            assert len(indices_list_kwargs) == 1, (
                "Only 1 set of indices to plot, so can only accept one set of index kwargs"
            )
    else:
        is_list_of_lists = [np.array(i).size for i in indices]
        is_list_of_lists = list(set(is_list_of_lists))
        if is_list_of_lists != [1]:
            assert split_on is None, (
                "You can only specify `split_on` when you are not providing list of lists inputs to `indices`."
            )
            tags = [i for i, _ in enumerate(indices)]
            if indices_list_kwargs is not None:
                assert len(indices) == len(indices_list_kwargs), (
                    "Must provide same number of sets of edges "
                    f"(currently len(indices) = {len(indices)}) as edge kwargs"
                    f"(currently len(indices_list_kwargs) = {len(indices_list_kwargs)}"
                )
                for idx, k in enumerate(indices_list_kwargs):
                    if k is None:
                        indices_list_kwargs[idx] = {}
            else:
                indices_list_kwargs = [{} for _ in indices]
        else:
            tags = [None]
            indices = [indices]
            indices_list_kwargs = [{}]

    extra_warning_message = ""
    if axes is None:
        axes = data.columns.to_numpy()
        # drop the splitting column if used
        if split_on_column:
            axes = np.delete(axes, np.where(axes == split_on))
            extra_warning_message += (
                "\n(One axis was removed because it is already used by `split_on`)"
            )

    if vmins is not None:
        assert len(axes) == len(vmins), (
            "Must specify a vmin (`vmins`) for every axis (`axes`). "
            f"Currently have {len(vmins)} vmins specified and {len(axes)} axes."
            f"{extra_warning_message}"
        )

    if vmaxes is not None:
        assert len(axes) == len(vmaxes), (
            "Must specify a vmax (`vmaxes`) for every axis (`axes`). "
            f"Currently have {len(vmaxes)} vmaxes specified and {len(axes)} axes."
            f"{extra_warning_message}"
        )

    p2cp = P2CP(data=data)
    p2cp.set_axes(
        columns=axes, angles=None, vmins=vmins, vmaxes=vmaxes, start_angle=orient_angle
    )

    for i, ind in enumerate(indices):
        # resolve kwarg priorities
        collated_kwargs = indices_list_kwargs[i].copy()
        for k in list(all_edge_kwargs.keys()):
            if k in collated_kwargs:
                warnings.warn(
                    f"Specified kwarg {k} in `all_edge_kwargs` but already set as kwarg for "
                    f"indices list index {i} with `indices_list_kwargs`. "
                    f"Disregarding `all_edge_kwargs` here.",
                    stacklevel=2,
                )
            else:
                collated_kwargs[k] = all_edge_kwargs[k]

        p2cp.build_edges(indices=ind, tag=tags[i], **collated_kwargs)

    return p2cp


def indices_for_unique_values(
    df: pd.DataFrame, column: Hashable
) -> Dict[Hashable, np.ndarray]:
    """
    Find the indices corresponding to each unique value in a column of a ``pandas`` dataframe.

    Works when the values contained in ``column`` are numerical *or* categorical.

    :param df: dataframe from which to find index values.
    :param column: column of the dataframe to use to find indices corresponding to each of the column's unique values.
    :return: ``dict`` whose keys are the unique values in the column of data and whose values are 1d arrays of index
        values.
    """
    return df.groupby(column).groups


def split_df_on_variable(
    df: pd.DataFrame,
    column: Hashable,
    cutoffs: Union[List[float], int],
    labels: Optional[Union[List[Hashable], np.ndarray]] = None,
) -> np.ndarray:
    """
    Generate value for each record in a dataframe according to a splitting criterion.

    Using either specified cutoff values or a specified number of quantiles for ``cutoffs``, return an ``(n, 1)``
    ``np.ndarray`` where the ith value corresponds to the partition assignment of the ith record of ``df``.

    If ``column`` corresponds to numerical data, and a ``list`` of ``cutoffs`` is provided, then dataframe records will
    be assigned according to the following binning scheme:

    (-inf, ``cutoff[0]``], (``cutoff[0]``, ``cutoff[1]``], ... , (``cutoff[-1]``, inf]

    If ``column`` corresponds to numerical data, and ``cutoffs`` is provided as an ``int``, then dataframe records will
    be assigned into ``cutoffs`` equal-sized quantiles.

    .. note::
        This method currently only supports splits where ``column`` corresponds to *numerical* data. For splits on
        categorical data values, see :py:func:`~hiveplotlib.p2cp.indices_for_unique_values()`.

    :param df: dataframe whose records will be assigned to a partition.
    :param column: column of the dataframe to use to assign partition of records.
    :param cutoffs: cutoffs to use in partitioning records according to the data under ``column``. When provided as a
        ``list``, the specified cutoffs will partition according to
        (-inf, ``cutoffs[0]``], `(`cutoffs[0]``, ``cutoffs[1]``], ... , (``cutoffs[-1]``, inf).
        When provided as an ``int``, the exact numerical break points will be determined to create ``cutoffs``
        equally-sized quantiles.
    :param labels: labels assigned to each bin. Default ``None`` labels each bin as a string based on its range of
        values. Note, when ``cutoffs`` is a list, ``len(labels)`` must be 1 greater than ``len(cutoffs)``. When
        ``cutoffs`` is an ``int``, ``len(labels)`` must be equal to ``cutoffs``.
    :return: ``(n, 1)`` ``np.ndarray`` whose values are partition assignments corresponding to records in ``df``.
    """
    # int cutoffs dictates quantile cut, otherwise cut
    if not isinstance(cutoffs, int):
        if labels is not None:
            assert len(labels) == len(cutoffs) + 1, (
                "Must have 1 more label than `cutoffs` (n cutoffs => n + 1 bins)"
            )

        bins = [-np.inf, *cutoffs, np.inf]
        # create pandas categorical array with binning information
        bin_cuts = pd.cut(df[column].values, bins=bins, labels=labels)
    else:
        if labels is not None:
            assert len(labels) == cutoffs, (
                "Must have 1 label per `cutoffs` (n quantiles => n labels)"
            )

        bin_cuts = pd.qcut(df[column].values, q=cutoffs, labels=labels)

    # convert to np array with shape `df.shape[0]` whose values are bin assignments (labels)
    return bin_cuts.to_numpy()
