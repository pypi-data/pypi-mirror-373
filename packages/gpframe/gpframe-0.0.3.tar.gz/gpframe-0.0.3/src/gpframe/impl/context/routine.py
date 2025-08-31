from ...api.contexts import RoutineContext

from ..syncm import SynchronizedMapUpdater, SynchronizedMapReader

def create_routine_context(
        frame_name: str,
        logger_name: str,
        routine_in_subprocess: bool,
        environment_reader: SynchronizedMapReader,
        request_reader: SynchronizedMapReader,
        event_msg_reader: SynchronizedMapReader,
        routine_msg_updater: SynchronizedMapUpdater,
) -> RoutineContext:
    
    class _Interface(RoutineContext):
        __slots__ = ()
        @property
        def frame_name(self) -> str:
            return frame_name
        @property
        def logger_name(self) -> str:
            return logger_name
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
        def event_msg(self) -> SynchronizedMapReader:
            return event_msg_reader
        @property
        def routine_msg(self) -> SynchronizedMapUpdater:
            return routine_msg_updater
        def __reduce__(self):
            return (
                create_routine_context,
                (frame_name,
                 logger_name,
                 routine_in_subprocess,
                 environment_reader,
                 request_reader,
                 event_msg_reader,
                 routine_msg_updater)
            )
        
    interface = _Interface()
    
    return interface



