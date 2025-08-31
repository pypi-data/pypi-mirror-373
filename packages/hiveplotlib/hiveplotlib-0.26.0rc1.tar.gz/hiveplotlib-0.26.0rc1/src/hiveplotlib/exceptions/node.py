"""
Custom exceptions for nodes.
"""


class RepeatUniqueNodeIDsError(Exception):
    """
    Raise a custom exception when non-unique node IDs are provided in a ``NodeCollection`` instance.

    Node IDs must be unique in a ``NodeCollection`` instance.
    """
