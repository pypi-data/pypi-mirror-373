import logging

from ...api.contexts import Controller

from ..syncm import SynchronizedMapUpdater, SynchronizedMapReader
from ..result import RoutineResult

def create_controller_context(
        frame_name: str,
        logger: logging.Logger,
        routine_in_subprocess,
        environment_reader: SynchronizedMapReader,
        request_updater: SynchronizedMapUpdater,
        event_msg_reader: SynchronizedMapReader,
        routine_msg_reader: SynchronizedMapReader,
        routine_result_reader: RoutineResult,
        routine_is_running_fn,
        routine_stop_fn
) -> Controller:
    
    class _Interface(Controller):
        __slots__ = ()
        @property
        def frame_name(self) -> str:
            return frame_name
        @property
        def logger(self) -> logging.Logger:
            return logger
        @property
        def routine_in_subprocess(self) -> bool:
            return routine_in_subprocess
        @property
        def environment(self) -> SynchronizedMapReader:
            return environment_reader
        @property
        def request(self) -> SynchronizedMapUpdater:
            return request_updater
        @property
        def event_msg(self) -> SynchronizedMapReader:
            return event_msg_reader
        @property
        def routine_msg(self) -> SynchronizedMapReader:
            return routine_msg_reader
        @property
        def routine_result(self) -> RoutineResult:
            return routine_result_reader
        @property
        def routine_is_running(self) -> bool:
            return routine_is_running_fn()
        def stop(self, **kwargs) -> None:
            routine_stop_fn(frame_name, logger, **kwargs)
    interface = _Interface()
    
    return interface


