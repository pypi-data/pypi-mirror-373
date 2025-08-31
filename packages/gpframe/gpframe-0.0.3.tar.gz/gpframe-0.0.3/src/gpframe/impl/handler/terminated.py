

import asyncio
import inspect
import threading
from typing import Awaitable, Callable, Union, cast

from ...api.outcome import Outcome

from .errors import FrameHandlerError

TerminatedHandler = Union[
    Callable[[Outcome], bool],
    Callable[[Outcome], Awaitable[bool]]
]

TerminatedHandlerAsync = Callable[[Outcome], Awaitable[bool]]

class TerminatedHandlerWrapper:
    __slots__ = ('_caller',)
    def __init__(self):
        self._caller: TerminatedHandlerAsync | None  = None
    
    async def __call__(self, outcome: Outcome) -> bool:
        if self._caller is not None:
            try:
                return await self._caller(outcome)
            except Exception as e:
                raise FrameHandlerError('terminated callback', e)
        return False
        
    def set_handler(self, handler: TerminatedHandler):
        if inspect.iscoroutinefunction(handler):
            self._caller = handler
        else:
            async def sync_caller(outcome: Outcome) -> bool:
                return cast(bool, await asyncio.to_thread(handler, outcome))
            self._caller = sync_caller

