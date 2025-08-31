from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Protocol

import inspect
import logging

from ..api.gpframe import FrameType
from ..api.outcome import Outcome

from .execute.base import RoutineExecution
from .execute.synchronize import SyncRoutineExecution
from .execute.ansynchronize import AsyncRoutineExecution
from .execute.subprocess import SubprocessRoutineExecution

from .state import _create_usage_state_role
from .state import _RoleTOC as _UsageStateRoleTOC

from .handler.redo import RedoHandlerWrapper
from .handler.redo import RedoHandler

from .handler.exception import ExceptionHandlerWrapper
from .handler.exception import ExceptionHandler

from .syncm import SynchronizedMap, SynchronizedMapReader, SynchronizedMapUpdater

from .context.controller import Controller, create_controller_context
from .context.event import EventContext, create_event_context
from .context.routine import RoutineContext, create_routine_context

from .result import RoutineResultSource

from .handler.event import EventHandlerWrapper
from .handler.event import EventHandler

from .outcome import OutcomeSource

from .handler.terminated import TerminatedHandlerWrapper
from .handler.terminated import TerminatedHandler

from .errors import HandledError

class TerminatedError(Exception):
    """Raised when accessing a context resource after frame termination.

    This error is thrown if a ``SynchronizedMapReader``/``SynchronizedMapUpdater``
    (or similar context-managed resource) is accessed after the frame has
    already terminated. It prevents use of stale or invalid state once
    the frame lifecycle has ended.
    """

class NotTerminatedError(Exception):
    """Raised when requesting an outcome before frame termination.

    This error occurs if ``FrameType.get_outcome()`` is called while the
    frame is still running. An outcome is only available once the frame has
    fully terminated.
    """


Routine = Callable[[RoutineContext], Any] | Callable[[RoutineContext], Awaitable[Any]]
RoutineCaller = Callable[[asyncio.AbstractEventLoop], tuple[Any, Exception | asyncio.CancelledError | None]]

class _ConstantTOC(Protocol):
    ALL_EVENTS: tuple[str, ...]

class _StateTOC(Protocol):
    usage: _UsageStateRoleTOC
    
    frame_name: str
    logger: logging.Logger

    event_handlers: dict[str, EventHandlerWrapper]
    redo_handler: RedoHandlerWrapper
    exception_handler: ExceptionHandlerWrapper
    
    environments: dict
    requests: dict

    routine_timeout: float | None
    cleanup_timeout: float | None

    routine_execution: RoutineExecution | None

    environment_map: SynchronizedMap | None
    request_map: SynchronizedMap | None
    event_msg_map: SynchronizedMap | None
    routine_msg_map: SynchronizedMap | None
    routine_result: RoutineResultSource | None

    outcome_source: OutcomeSource | None
    
    terminated_callback: TerminatedHandlerWrapper



class _CoreTOC(Protocol):
    def initialize(self) -> None:
        ...
    
    def create_routine_execution(self, as_subprocess: bool) -> RoutineExecution:
        ...
    
    def _get_updater_reader(self, syncm: SynchronizedMap) -> tuple[SynchronizedMapUpdater, SynchronizedMapReader]:
        ...
    
    def create_messages(self, routine_execution: RoutineExecution) -> tuple[Controller, EventContext, RoutineContext]:
        ...
    
    def _struct_outcome(self, frame_error: Exception | None, handler_error: Exception | None) -> None:
        ...
    
    def _cleanup_maps(self) -> None:
        ...
    
    async def frame(self, routine_caller: RoutineCaller, emsg: EventContext, rmsg: RoutineContext) -> None:
        ...

class _RoleTOC(Protocol):
    constant: _ConstantTOC
    state: _StateTOC
    core: _CoreTOC
    interface: FrameType


def create_frame_role(routine: Routine):

    if not callable(routine):
        raise TypeError("routine must be a callable")

    class _Constant(_ConstantTOC):
        __slots__ = ()
        ALL_EVENTS = (
            'on_open',
            'on_start',
            'on_end',
            'on_cancel',
            'on_close'
        )
    constant = _Constant()

    class _State(_StateTOC):
        __slots__ = ()
        usage: _UsageStateRoleTOC = _create_usage_state_role()
        
        frame_name: str = "noname"
        logger: logging.Logger = logging.getLogger("gpframe")

        event_handlers: dict[str, EventHandlerWrapper] = {}
        redo_handler: RedoHandlerWrapper = RedoHandlerWrapper()
        exception_handler: ExceptionHandlerWrapper = ExceptionHandlerWrapper()

        environments: dict = {}
        requests: dict = {}

        routine_timeout: float | None
        cleanup_timeout: float | None

        routine_execution: RoutineExecution | None

        environment_map: SynchronizedMap | None = None
        request_map: SynchronizedMap | None = None
        event_msg_map: SynchronizedMap | None  = None
        routine_msg_map: SynchronizedMap | None = None
        routine_result: RoutineResultSource | None = None

        outcome_source: OutcomeSource | None = None

        terminated_callback = TerminatedHandlerWrapper()

    state = _State()

    class _Core(_CoreTOC):
        __slots__ = ()
        def initialize(self) -> None:
            state.event_handlers.update({
                event_name : EventHandlerWrapper(event_name)
                for event_name in constant.ALL_EVENTS
            })
        
        def create_routine_execution(self, as_subprocess: bool) -> RoutineExecution:
            frame_name = state.frame_name
            logger = state.logger
            if inspect.iscoroutinefunction(routine):
                if as_subprocess:
                    raise TypeError("async function can not be subprocess.")
                return AsyncRoutineExecution(frame_name, logger)
            else:
                if as_subprocess:
                    return SubprocessRoutineExecution(frame_name, logger)
                else:
                    return SyncRoutineExecution(frame_name, logger)
        
        def _get_updater_reader(self, syncm: SynchronizedMap) -> tuple[SynchronizedMapUpdater, SynchronizedMapReader]:
            return syncm.updater, syncm.reader
        
        def create_messages(self, routine_execution: RoutineExecution) -> tuple[Controller, EventContext, RoutineContext]:
            def access_validator():
                if state.usage.interface.terminated:
                    raise TerminatedError
            
            lock = routine_execution.get_shared_lock()
            map_factory = routine_execution.get_shared_map_factory()

            state.environment_map = SynchronizedMap(lock, map_factory(state.environments), access_validator)
            state.request_map = SynchronizedMap(lock, map_factory(state.requests), access_validator)
            state.event_msg_map = SynchronizedMap(lock, map_factory(), access_validator)
            state.routine_msg_map = SynchronizedMap(lock, map_factory(), access_validator)

            _, env_reader = self._get_updater_reader(state.environment_map)
            req_updater, req_reader = self._get_updater_reader(state.request_map)
            emsg_updater, emsg_reader = self._get_updater_reader(state.event_msg_map)
            rmsg_updater, rmsg_reader = self._get_updater_reader(state.routine_msg_map)

            routine_result = RoutineResultSource(lock, access_validator)
            routine_result_reader = routine_result.interface
            state.routine_result = routine_result

            as_subprocess = isinstance(routine_execution, SubprocessRoutineExecution)
            
            controller_msg = create_controller_context(
                state.frame_name,
                state.logger,
                as_subprocess,
                env_reader,
                req_updater,
                emsg_reader,
                rmsg_reader,
                routine_result_reader,
                routine_execution.routine_is_running,
                routine_execution.request_stop_routine)
            event_msg = create_event_context(
                state.frame_name,
                state.logger,
                as_subprocess,
                env_reader,
                req_reader,
                emsg_updater,
                rmsg_reader,
                routine_result_reader)
            routine_msg = create_routine_context(
                state.frame_name,
                state.logger.name,
                as_subprocess,
                env_reader,
                req_reader,
                emsg_reader,
                rmsg_updater)
            
            return controller_msg, event_msg, routine_msg
        

        def _struct_outcome(
                self,
                frame_error: Exception | None,
                handler_error: Exception | None
            ) -> None:
            assert state.routine_result
            routine_result = state.routine_result.get_routine_result_unsafe()
            routine_error = state.routine_result.get_routine_error_unsafe()
            assert state.request_map
            requests = state.request_map.copy_map_without_usage_state_check()
            assert state.event_msg_map
            event_msg = state.event_msg_map.copy_map_without_usage_state_check()
            assert state.routine_msg_map
            routine_msg = state.routine_msg_map.copy_map_without_usage_state_check()

            state.outcome_source = OutcomeSource(
                routine_result,
                routine_error,
                frame_error,
                handler_error,
                requests,
                event_msg,
                routine_msg)
        
        def _cleanup_maps(self) -> None:
            assert state.environment_map
            state.environment_map.clear_map_unsafe()
            assert state.request_map
            state.request_map.clear_map_unsafe()
            assert state.event_msg_map
            state.event_msg_map.clear_map_unsafe()
            assert state.routine_msg_map
            state.routine_msg_map.clear_map_unsafe()
            assert state.routine_result
            state.routine_result.clear_routine_result_unsafe()
            state.routine_result.clear_routine_error_unsafe()
        
        
        async def frame(self, emsg: EventContext, rmsg: RoutineContext) -> None:
            frame_error = None
            handler_error = None
            try:
                if state.routine_execution is None:
                    raise RuntimeError("state.routine_execution is None")
                routine_execution = state.routine_execution

                frame_name = state.frame_name
                logger = state.logger
                
                ev_handlers = state.event_handlers

                try:
                    await ev_handlers["on_open"](emsg)
                except HandledError as e:
                    if not await asyncio.shield(state.exception_handler(emsg, e)):
                        raise
                
                while True:
                    try:
                        await ev_handlers["on_start"](emsg)
                    except HandledError as e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise
                    
                    try:
                        routine_execution.load_routine(frame_name, logger, routine, rmsg)
                    except HandledError as e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise

                    try:
                        result, e = routine_execution.wait_routine_result(frame_name, logger)
                    except HandledError as e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise

                    if isinstance(e, asyncio.CancelledError):
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise
                        else:
                            e = None
                    
                    if e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise
                        
                    
                    assert state.routine_result
                    state.routine_result.set(result, e)
                    
                    try:
                        await ev_handlers["on_end"](emsg)
                    except HandledError as e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise
                    
                    try:
                        redo = await state.redo_handler(emsg)
                    except HandledError as e:
                        if not await asyncio.shield(state.exception_handler(emsg, e)):
                            raise

                    if not redo:
                        break

            except asyncio.CancelledError as e:
                try:
                    await asyncio.shield(ev_handlers["on_cancel"](emsg))
                except HandledError as e:
                    if not await asyncio.shield(state.exception_handler(emsg, e)):
                        raise
            finally:
                try:
                    await asyncio.shield(ev_handlers["on_close"](emsg))
                except HandledError as e:
                    if not await asyncio.shield(state.exception_handler(emsg, e)):
                        raise

                def to_terminate():
                    core._struct_outcome(frame_error, handler_error)

                state.usage.interface.terminate(to_terminate)

                core._cleanup_maps()
                routine_execution.cleanup(frame_name, logger)

                try:
                    assert state.outcome_source
                    await asyncio.shield(state.terminated_callback(state.outcome_source.interface))
                except HandledError as e:
                    if not await asyncio.shield(state.exception_handler(emsg, e)):
                        raise
    core = _Core()

    class _Interface(FrameType):
        __slots__ = ()
        def set_name(self, name: str) -> None:
            def fn():
                state.frame_name = name
            state.usage.interface.load(fn)
    
        def set_logger(self, logger: logging.Logger):
            def fn():
                state.logger = logger
            state.usage.interface.load(fn)

        def set_environments(self, environments: dict):
            def fn():
                state.environments = dict(environments)
            state.usage.interface.load(fn)
        
        def set_requests(self, requests: dict):
            def fn():
                state.requests = dict(requests)
            state.usage.interface.load(fn)
        
        def set_exception_handler(self, handler: ExceptionHandler):
            def fn():
                state.exception_handler.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_terminated_callback(self, handler: TerminatedHandler):
            def fn():
                state.terminated_callback.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_redo_handler(self, handler: RedoHandler):
            def fn():
                state.redo_handler.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_open(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_open"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_start(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_start"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_end(self, handler:EventHandler) -> None:
            def fn():
                state.event_handlers["on_end"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_cancel(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_cancel"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_close(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_close"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_routine_timeout(self, timeout: float | None) -> None:
            def fn():
                state.routine_timeout = timeout
            state.usage.interface.load(fn)
        
        def set_cleanup_timeout(self, timeout: float | None) -> None:
            def fn():
                state.cleanup_timeout = timeout
            state.usage.interface.load(fn)
        
        def start(self, *, as_subprocess: bool = False) -> tuple[Controller, asyncio.Task[None]]:
            state.usage.interface.activate()
            state.routine_execution = core.create_routine_execution(as_subprocess)
            ctrl, emsg, rmsg = core.create_messages(state.routine_execution)
            task = asyncio.create_task(core.frame(emsg, rmsg))
            return ctrl, task
        
        def get_outcome(self) -> Outcome:
            if state.usage.interface.terminated:
                assert state.outcome_source
                return state.outcome_source.interface
            else:
                raise NotTerminatedError
            
        def peek_outcome(self) -> Outcome | None:
            if state.usage.interface.terminated:
                assert state.outcome_source
                return state.outcome_source.interface
            else:
                return None
    interface = _Interface()

    @dataclass(slots = True)
    class _Role(_RoleTOC):
        constant: _ConstantTOC
        state: _StateTOC
        core: _CoreTOC
        interface: FrameType
    
    return _Role(constant = constant, state = state, core = core, interface = interface)


