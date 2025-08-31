import logging

from ...api.contexts import EventContext

from ..syncm import SynchronizedMapUpdater, SynchronizedMapReader
from ..result import RoutineResult


def create_event_context(
        frame_name: str,
        logger: logging.Logger,
        routine_in_subprocess,
        environment_reader: SynchronizedMapReader,
        request_reader: SynchronizedMapReader,
        event_msg_updater: SynchronizedMapUpdater,
        routine_msg_reader: SynchronizedMapReader,
        routine_result_reader: RoutineResult
) -> EventContext:
    
    class _Interface(EventContext):
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
        def request(self) -> SynchronizedMapReader:
            return request_reader
        @property
        def event_msg(self) -> SynchronizedMapUpdater:
            return event_msg_updater
        @property
        def routine_msg(self) -> SynchronizedMapReader:
            return routine_msg_reader
        @property
        def routine_result(self) -> RoutineResult:
            return routine_result_reader
        
    interface = _Interface()
    
    return interface

