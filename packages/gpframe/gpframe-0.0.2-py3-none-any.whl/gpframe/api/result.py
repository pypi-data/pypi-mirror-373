"""
Sentinel value for missing routine results.

This module defines the constant ``NO_VALUE`` to represent the absence of a
routine return value. It is the initial value before a routine produces a result,
and it remains unchanged in the following cases:

- The routine has not yet executed
- The routine was canceled
- The routine was interrupted
- The routine raised an exception

By comparing a routine's return value with ``NO_VALUE``, callers can detect
whether the routine produced a valid result.
"""

from enum import Enum

class NO_VALUE(Enum):
    """
    Sentinel value for missing routine results.

    This constant represents the absence of a routine return value. It is the
    initial value before a routine produces a result, and it remains unchanged
    in the following cases:

    - The routine has not yet executed
    - The routine was canceled
    - The routine was interrupted
    - The routine raised an exception

    By comparing a routine's return value with ``NO_VALUE``, callers can detect
    whether the routine produced a valid result.

    Note:
        This is defined as an Enum class, but is intended to be used directly
        as a sentinel value.
    """
    pass


