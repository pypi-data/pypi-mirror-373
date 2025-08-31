"""
Unified routine execution framework with frames, events, and contexts.

gpframe wraps user-defined routines with a *frame* that provides lifecycle
management, event handling, re-execution, and shared state. The routine itself
can remain a simple function or async function, while the frame coordinates
control flow and consistency.

Key features:
    - Works generically, from simple processes to event-driven extensions
      and parallel execution control
    - Supports both synchronous and asynchronous routines
    - Synchronous routines can optionally be executed in subprocesses
      (asynchronous ones are excluded)

Execution flow:
    - on_start → routine execution → on_end → redo check (continue or finish)
    - on_cancel is called when canceled
    - on_close is always called upon termination, followed by the terminated callback

Data and error handling:
    - Results, errors, and message exchange are consolidated into an ``Outcome``
    - Exceptions from routines, frames, and event handlers are distinguished,
      and which to re-raise is controlled by ``Raises``
    - Shared data (environment, requests, event messages) is managed with
      synchronized maps to ensure consistency across contexts
    - Contexts (``ControllerContext``, ``EventContext``, ``RoutineContext``)
      provide safe and structured access during execution

Main components:
    - **Frame** — entry point that wraps and manages routines
    - **ControllerContext / EventContext / RoutineContext** — execution contexts
    - **Outcome** — holds results, errors, requests, and messages
    - **Raises** — selects which exception types to re-raise
    - **Error types** — ``FrameError``, ``TerminatedError``, ``NotTerminatedError``, etc.

gpframe provides unified control features without burdening the routine itself.
"""
from .api.gpframe import Frame

from .api.gpframe import FrameType

from .api.contexts import Controller
from .api.contexts import EventContext
from .api.contexts import RoutineContext

from .api.outcome import Outcome

from .api.result import NO_VALUE

from .impl.frame import TerminatedError, NotTerminatedError

from .impl.execute.ansynchronize import FutureTimeoutError, ThreadCleanupTimeoutError
from .impl.execute.subprocess import SubprocessTimeoutError

from .impl.handler.exception import Throw

__all__ = ("Frame", "FrameType",
           "Controller", "EventContext", "RoutineContext",
           "Outcome",
           "NO_VALUE",
           "TerminatedError", "NotTerminatedError",
           "FutureTimeoutError", "ThreadCleanupTimeoutError",
           "SubprocessTimeoutError",
           "Throw")
