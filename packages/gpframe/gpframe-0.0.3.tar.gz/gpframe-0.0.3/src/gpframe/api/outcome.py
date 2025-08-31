"""
Result container abstraction for routine execution.

This module defines the abstract class ``Outcome``, which
represents the result of a routine execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import MappingProxyType

class Outcome(ABC):
    """
    Interface representing the result of a frame execution.

    It is used to collectively reference the return value and errors  
    from a routine, as well as related messages obtained during  
    a single frame execution.

    The provided maps of requests and messages are snapshots taken  
    at the end of the frame and are read-only.
    """
    __slots__ = ()
    @property
    @abstractmethod
    def routine_result(self) -> Any:
        """The value returned by the routine, or ``NO_VALUE`` if none was produced."""
    @property
    @abstractmethod
    def routine_error(self) -> Exception | None:
        """Exception raised inside the routine, or ``None`` if successful."""
    @property
    @abstractmethod
    def frame_error(self) -> Exception | None:
        """Exception raised during frame control, or ``None`` if none."""
    @property
    @abstractmethod
    def handler_error(self) -> Exception | None:
        """Exception raised in an event handler, or ``None`` if none."""
    @property
    @abstractmethod
    def requests(self) -> MappingProxyType:
        """Snapshot of the requests map (read-only)."""
    @property
    @abstractmethod
    def event_messages(self) -> MappingProxyType:
        """Snapshot of the event messages map (read-only)."""
    @property
    @abstractmethod
    def routine_messages(self) -> MappingProxyType:
        """Snapshot of the routine messages map (read-only)."""
    @property
    @abstractmethod
    def has_error(self) -> bool:
        """True if any error (routine, frame, or handler) occurred."""
