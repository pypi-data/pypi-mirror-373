"""
Custom exceptions for hive plots.
"""


class InvalidPartitionVariableError(Exception):
    """
    Raise a custom exception when an invalid ``partition_variable`` is provided in a ``HivePlot`` instance.

    Partition variables must be one of the columns in the ``nodes.data`` attribute.
    """


class MissingSortingVariableError(Exception):
    """
    Raise a custom exception when an axis in a ``HivePlot`` instance is not provided a ``sorting_variable``.
    """


class RepeatInPartitionAxisNameError(Exception):
    """
    Raise a custom exception when an axis in a ``HivePlot`` instance is going to be named ending with ``_repeat``.

    This naming convention is reserved for repeat axes in ``HivePlot`` internals.
    """


class InvalidAxisNameError(Exception):
    """
    Raise a custom exception when the user specifies an invalid axis name in a ``HivePlot`` instance.
    """


class InvalidEdgeKwargHierarchyError(Exception):
    """
    Raise a custom exception when the user specifies an invalid edge hierarchy for a ``HivePlot`` instance.
    """


class InvalidAxesOrderError(Exception):
    """
    Raise a custom exception when the user specifies an invalid ``axes_order``.

    A provided axes ordering must include all of the names corresponding to the partition set via the provided
    ``partition_variable`` in a ``HivePlot`` instance.
    """


class InvalidSortingVariableError(Exception):
    """
    Raise a custom exception when an invalid ``sorting_variable`` is provided in a ``HivePlot`` instance.

    Sorting variables must be one of the columns in the ``nodes.data`` attribute.
    """


class InvalidHoverVariableError(Exception):
    """
    Raise a custom exception when an invalid hover variable is provided when plotting a ``HivePlot`` instance.

    Hover information is only supported for ``"nodes"``, ``"axes"``, and / or ``"edges"``.
    """


class InvalidVizBackendError(Exception):
    """
    Raise a custom exception when an invalid viz back end is provided when setting a ``HivePlot`` instance viz back end.
    """


class UnspecifiedTagError(Exception):
    """
    Raise a custom exception when a tag is not specified but the tag cannot be inferred because there are multiple tags.
    """
