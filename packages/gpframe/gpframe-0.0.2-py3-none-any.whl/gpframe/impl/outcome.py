from __future__ import annotations

from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import Any

from ..api.outcome import Outcome

class OutcomeSource:
    __slots__ = (
        "_routine_result",
        "_routine_error", "_frame_error", "_handler_error",
        "_requests", "_event_messages", "_routine_messages",
        "_reader")
    def __init__(
            self,
            routine_result: Any,
            routine_error: Exception | None,
            frame_error: Exception | None,
            handler_error: Exception | None,
            requests: dict,
            event_messages: dict,
            routine_messages: dict
        ):
        self._routine_result = routine_result
        self._routine_error = routine_error
        self._frame_error = frame_error
        self._handler_error = handler_error
        self._requests = MappingProxyType(requests)
        self._event_messages = MappingProxyType(event_messages)
        self._routine_messages = MappingProxyType(routine_messages)
        self._reader = self._create_reader()
    
    def _create_reader(self) -> Outcome:
        outer = self
        class _Interface(Outcome):
            __slots__ = ()
            @property
            def routine_result(self) -> Any:
                return outer._routine_result
            @property
            def routine_error(self) -> Exception | None:
                return outer._routine_error
            @property
            def frame_error(self) -> Exception | None:
                return outer._frame_error
            @property
            def handler_error(self) -> Exception | None:
                return outer._handler_error
            @property
            def requests(self) -> MappingProxyType:
                return outer._requests
            @property
            def event_messages(self) -> MappingProxyType:
                return outer._event_messages
            @property
            def routine_messages(self) -> MappingProxyType:
                return outer._routine_messages
            @property
            def has_error(self) -> bool:
                return any(e is not None for e in (outer._routine_error, outer._frame_error, outer._handler_error))
        return _Interface()
    
    @property
    def interface(self) -> Outcome:
        return self._reader

