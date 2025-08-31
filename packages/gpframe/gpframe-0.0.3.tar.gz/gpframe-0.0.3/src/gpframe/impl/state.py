from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Callable, Protocol, Type


class UsageState(ABC):
    __slots__ = ()

    @abstractmethod
    def load(self, fn: Callable[[], Any]) -> Any:
        ...

    @abstractmethod
    def activate(self) -> Any:
        ...
    
    @abstractmethod
    def modify(self, fn: Callable[[], Any]) -> Any:
        ...
    
    @abstractmethod
    def terminate(self, fn: Callable[[], Any]) -> Any:
        ...
    
    @property
    @abstractmethod
    def terminated(self) -> bool:
        ...

class UnknownStateErrorBase(Exception, ABC):
    pass

class InvalidStateErrorBase(Exception, ABC):
    pass

class TerminatedErrorBase(Exception, ABC):
    pass


class _ConstantTOC(Protocol):
    UnknownStateError: Type[UnknownStateErrorBase]
    InvalidStateError: Type[InvalidStateErrorBase]
    TerminatedError: Type[TerminatedErrorBase]
    UsageState: Enum

class _StateTOC(Protocol):
    lock: Lock
    current_state: Enum

class _CoreTOC(Protocol):
    def validate_state_value(self, state: Enum) -> None:
        ...
    
    def require_state(self, expected: Enum) -> None:
        ...

    def transit_state_unsafe(self, to: Enum) -> None:
        ...

    def transit_state_with(self, to: Enum, fn: Callable[[], Any]) -> Any:
        ...

    def transit_state(self, to: Enum) -> None:
        ...

class _RoleTOC(Protocol):
    constant: _ConstantTOC
    state: _StateTOC
    core: _CoreTOC
    interface: UsageState

def _create_usage_state_role():
    
    class _Constant(_ConstantTOC):
        __slots__ = ()
        class UnknownStateError(UnknownStateErrorBase):
            pass
        class InvalidStateError(InvalidStateErrorBase):
            pass
        class TerminatedError(TerminatedErrorBase):
            pass
        class UsageState(Enum):
            LOAD = "LOAD"
            ACTIVE = "ACTIVE"
            TERMINATED = "TERMINATED"
    constant = _Constant()

    class _State(_StateTOC):
        __slots__ = ()
        lock = Lock()
        current_state = constant.UsageState.LOAD
    state = _State()

    class _Core(_CoreTOC):
        __slots__ = ()
        def validate_state_value(self, state: object):
            if not isinstance(state, constant.UsageState):
                raise constant.UnknownStateError(
                    f"Unknown or unsupported state value: {state}")
        
        def require_state(self, expected: Enum) -> None:
            self.validate_state_value(expected)
            current_state = state.current_state
            if expected is not current_state:
                err_log = f"State error: expected = {expected}, actual = {current_state}"
                if current_state is constant.UsageState.TERMINATED:
                    raise constant.TerminatedError(err_log)
                raise constant.InvalidStateError(err_log)
        
        def maintain(self, keep: Enum, fn: Callable[[], Any]) -> Any:
            with state.lock:
                core.require_state(keep)
                return fn()
        
        def transit_state_unsafe(self, to: Enum) -> None:
            self.validate_state_value(to)
            us = constant.UsageState
            current_state = state.current_state
            to_active = current_state is us.LOAD and to is us.ACTIVE
            to_terminal = current_state is us.ACTIVE and to is us.TERMINATED
            if not (to_active or to_terminal):
                raise constant.InvalidStateError(
                    f"Invalid transition: {current_state} → {to}")
            state.current_state = to
        
        def transit_state_with(self, to: Enum, fn: Callable[[], Any]) -> Any:
            with state.lock:
                core.transit_state_unsafe(to)
                return fn()

        def transit_state(self, to: Enum) -> None:
            with state.lock:
                core.transit_state_unsafe(to)
    core = _Core()

    class _Interface(UsageState):
        __slots__ = ()
        def load(self, fn: Callable[[], Any]) -> Any:
            return core.maintain(constant.UsageState.LOAD, fn)

        def activate(self) -> None:
            core.transit_state(constant.UsageState.ACTIVE)
        
        def modify(self, fn: Callable[[], Any]) -> Any:
            return core.maintain(constant.UsageState.ACTIVE, fn)
        
        def terminate(self, fn: Callable[[], Any]) -> Any:
            return core.transit_state_with(constant.UsageState.TERMINATED, fn)
        
        @property
        def terminated(self) -> bool:
            with state.lock:
                return state.current_state is constant.UsageState.TERMINATED
        
    interface = _Interface()

    @dataclass(slots = True)
    class _Role(_RoleTOC):
        constant: _ConstantTOC
        state: _StateTOC
        core: _CoreTOC
        interface: UsageState
    
    return _Role(
        constant = constant,
        state = state,
        core = core,
        interface = interface
    )
