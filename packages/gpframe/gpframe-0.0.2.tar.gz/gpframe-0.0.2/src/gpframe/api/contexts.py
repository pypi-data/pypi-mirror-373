"""
contexts.py

Defines abstract context interfaces for controllers, event handlers,
and routines. These contexts provide structured access to logging,
shared state, and communication channels, making it clear which
elements are read-only and which are writable.

Design notes:
    - All contexts separate read-only and writable elements.
    - Logging is always available.
    - Shared state and message access are structured to prevent
      unintended interference.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from ..impl.result import RoutineResult
    from ..impl.syncm import SynchronizedMapReader, SynchronizedMapUpdater


class Controller(ABC):
    """Controller for running routine.

    Provides:
        - Read-only access to environment and inbound messages
        - Writable request channel
        - Routine result access
        - Lifecycle control (stop / is_running)

    Notes:
        - `environment`, `event_msg`, `routine_msg`, `routine_result` are read-only
        - `request` is the only writable channel
        - `stop()` is idempotent
    """
    __slots__ = ()
    @property
    @abstractmethod
    def frame_name(self) -> str:
        ...
    @property
    @abstractmethod
    def logger(self) -> Logger:
        ...
    @property
    @abstractmethod
    def routine_in_subprocess(self) -> bool:
        ...
    @property
    @abstractmethod
    def environment(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def request(self) -> SynchronizedMapUpdater:
        """Writable channel to send requests to the routine.

        This is a best-effort communication mechanism:
            - The routine may use these requests as hints or instructions.
            - There is no guarantee that any given request will be executed
            or even recognized.
            - Actual behavior depends on the routine's implementation.

        Use this as a way to suggest actions, not as a strict control channel.
        """
    @property
    @abstractmethod
    def event_msg(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_msg(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_result(self) -> RoutineResult:
        """Result container for the routine.

        Notes:
            - The `RoutineResult.value` field is initialized to `NO_VALUE`.
            - This remains `NO_VALUE` if the routine has not yet executed,
            or if it finished without producing a result.
            - Compare against `NO_VALUE` to detect these cases.
        """
    @abstractmethod
    def stop(self, *, kill: bool = False) -> None:
        """Request the routine to stop.

        Behavior depends on how the routine is executed:
            - Async routine: calls `cancel()`. If `kill=True`, the flag is ignored.
            - Subprocess routine: calls `terminate()`. If `kill=True`, calls `kill()` instead.
            - Synchronous in-process routine: not supported → raises TypeError.

        Args:
            kill: If True and the routine is a subprocess, use a hard kill instead
                of graceful termination. Ignored for async routines.

        Raises:
            TypeError: If the routine is a synchronous in-process function.
        """
    @property
    @abstractmethod
    def routine_is_running(self) -> bool:
        """Whether the routine appears to be running.

        Notes:
            - This value is an approximate indicator only.
            - It may not reflect the exact, real-time execution state.
            - Use it as a guideline rather than a strict guarantee.
        """



class EventContext(ABC):
    """Context used inside event handlers.

    Provides:
        - Read-only access to environment, request, routine messages, and results
        - Writable event message channel

    Notes:
        - `request` is read-only here (no sending)
        - `event_msg` is the only writable channel
    """
    __slots__ = ()
    @property
    @abstractmethod
    def frame_name(self) -> str:
        ...
    @property
    @abstractmethod
    def logger(self) -> Logger:
        ...
    @property
    @abstractmethod
    def routine_in_subprocess(self) -> bool:
        ...
    @property
    @abstractmethod
    def environment(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def request(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def event_msg(self) -> SynchronizedMapUpdater:
        ...
    @property
    @abstractmethod
    def routine_msg(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_result(self) -> RoutineResult:
        """Result container for the routine.

        Notes:
            - The `RoutineResult.value` field is initialized to `NO_VALUE`.
            - This remains `NO_VALUE` if the routine has not yet executed,
            or if it finished without producing a result.
            - Compare against `NO_VALUE` to detect these cases.
        """


class RoutineContext(ABC):
    """Context for routines executed by the system.

    Provides:
        - Read-only access to environment, request, and event messages
        - Writable routine message channel
        - Logger name and subprocess execution flag

    Notes:
        - When `executes_as_subprocess` is True, data must be serializable
        - `routine_msg` is the only writable channel
    """
    __slots__ = ()
    @property
    @abstractmethod
    def frame_name(self) -> str:
        ...
    @property
    @abstractmethod
    def logger_name(self) -> str:
        """Name of the logger channel associated with this routine.

        Unlike other contexts, a `Logger` instance is not provided directly.
        Instead, use this name to obtain a logger when needed.

        Reason:
            - Supports routines that may run in a separate subprocess,
            where direct logger objects cannot be shared safely.
        """
    @property
    @abstractmethod
    def routine_in_subprocess(self) -> bool:
        ...
    @property
    @abstractmethod
    def environment(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def request(self) -> SynchronizedMapUpdater:
        ...
    @property
    @abstractmethod
    def event_msg(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_msg(self) -> SynchronizedMapReader:
        ...
