# utils.py

"""
Utility functions for hive plot curvature and coordinates.
"""

from typing import List, Tuple, Union

import numpy as np


def cartesian2polar(
    x: Union[np.ndarray, float], y: Union[np.ndarray, float]
) -> Tuple[Union[np.ndarray, float], Union[np.ndarray, float]]:
    """
    Convert cartesian coordinates e.g. (x, y) to polar coordinates.

    (Polar coordinates e.g. (rho, phi), where `rho` is distance from origin, and `phi` is counterclockwise angle off of
    x-axis in degrees.)

    :param x: Cartesian x coordinates.
    :param y: Cartesian y coordinates.
    :return: (rho, phi) polar coordinates.
    """
    rho = np.sqrt(x**2 + y**2)
    phi = np.degrees(np.arctan2(y, x))
    return rho, phi


def polar2cartesian(
    rho: Union[np.ndarray, float], phi: Union[np.ndarray, float]
) -> Tuple[Union[np.ndarray, float], Union[np.ndarray, float]]:
    """
    Convert polar coordinates to cartesian coordinates e.g. (x, y).

    (Polar coordinates e.g. (rho, phi), where `rho` is distance from origin, and `phi` is counterclockwise angle off of
    x-axis in degrees.)

    :param rho: distance from origin.
    :param phi: counterclockwise angle off of x-axis in degrees (not radians).
    :return: (x, y) cartesian coordinates.
    """
    x = rho * np.cos(np.radians(phi))
    y = rho * np.sin(np.radians(phi))
    return x, y


def bezier(
    start: float, end: float, control: float, num_steps: int = 100
) -> np.ndarray:
    """
    Calculate 1-dimensional Bézier curve values between ``start`` and ``end`` with curve based on ``control``.

    Note, this function is hardcoded for exactly 1 control point.

    :param start: starting point.
    :param end: ending point.
    :param control: "pull" point.
    :param num_steps: number of points on Bézier curve.
    :return: ``(num_steps, )`` sized ``np.ndarray`` of 1-dimensional discretized Bézier curve output.
    """
    steps = np.linspace(0, 1, num_steps)
    return (1 - steps) ** 2 * start + 2 * (1 - steps) * steps * control + steps**2 * end


def bezier_all(
    start_arr: Union[List[float], np.ndarray],
    end_arr: Union[List[float], np.ndarray],
    control_arr: Union[List[float], np.ndarray],
    num_steps: int = 100,
) -> np.ndarray:
    """
    Calculate Bézier curve between multiple start and end values.

    Note, this function is hardcoded for exactly 1 control point per curve.

    :param start_arr: starting point of each curve.
    :param end_arr: corresponding ending point of each curve.
    :param control_arr: corresponding "pull" points for each curve.
    :param num_steps: number of points on each Bézier curve.
    :return: ``(start_arr * num_steps, )`` sized ``np.ndarray`` of 1-dimensional discretized Bézier curve output.
        Note, every ``num_steps`` chunk of the output corresponds to a different Bézier curve.
    """
    assert (
        np.array(start_arr).size == np.array(end_arr).size == np.array(control_arr).size
    ), "params `start_arr`, `end_arr`, and `control_arr` must be the same size"

    # each curve will be represented by the partitioning of the result by every `num_steps` index vals
    steps = np.tile(np.linspace(0, 1, num_steps), np.array(start_arr).size)

    # repeat each start, stop, and control value to multiply point-wise in one line
    start = np.repeat(start_arr, num_steps)
    end = np.repeat(end_arr, num_steps)
    control = np.repeat(control_arr, num_steps)

    return (1 - steps) ** 2 * start + 2 * (1 - steps) * steps * control + steps**2 * end
