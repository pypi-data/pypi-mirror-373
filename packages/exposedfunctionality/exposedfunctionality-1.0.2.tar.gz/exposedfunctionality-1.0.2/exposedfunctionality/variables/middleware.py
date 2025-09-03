"""
Middleware functions for variables exposed to the user

"""

from typing import (
    Optional,
    Union,
)
from .core import (
    ExposedValueData,
)


def min_max_clamp(
    value,
    valuedata: ExposedValueData,
    min: Optional[Union[int, float]] = None,  # pylint: disable=redefined-builtin
    max: Optional[Union[int, float]] = None,  # pylint: disable=redefined-builtin
):
    """Clamps a value between min and max

    Args:
        value (Any): Value to clamp
        valuedata (ExposedValueData): Value data
        min (Optional[Union[int, float]]): Minimum value. Defaults to None.
        max (Optional[Union[int, float]]): Maximum value. Defaults to None.

    Raises:
        ValueError: If max < min

    Returns:
        Any: Clamped value
    """

    if min is None:
        min = getattr(valuedata, "min", None)
    if max is None:
        max = getattr(valuedata, "max", None)

    if max is not None and min is not None and max < min:
        raise ValueError("max must be greater than or equal to min")
    if min is not None and value < min:
        return min
    if max is not None and value > max:
        return max
    return value
