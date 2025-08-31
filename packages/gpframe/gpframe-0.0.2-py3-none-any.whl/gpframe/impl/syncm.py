
from abc import ABC, abstractmethod
import threading
from typing import Any, Callable
from multiprocessing.managers import DictProxy

class SynchronizedMapUpdater(ABC):
    @abstractmethod
    def get(self, key: Any, default: Any = None) -> Any:
        ...
    @abstractmethod
    def update(self, key: Any, value: Any) -> None:
        ...
    @abstractmethod
    def remove(self, key: Any, default: Any = None) -> Any:
        ...
    @abstractmethod
    def __getitem__(self, key: Any) -> Any:
        ...

class SynchronizedMapReader(ABC):
    @abstractmethod
    def get(self, key: Any, default: Any = None) -> Any:
        ...

    @abstractmethod
    def __getitem__(self, key: Any) -> Any:
        ...


class SynchronizedMap:
    __slots__ = ("_usage_state_checker", "_lock", "_map", "_updater", "_reader")
    def __init__(
            self,
            lock: threading.Lock,
            map_: dict | DictProxy,
            usage_state_checker: Callable[[], None] | None = None
        ):
        self._usage_state_checker = usage_state_checker if usage_state_checker else lambda: None
        self._lock = lock
        self._map = map_
        self._updater = self._create_updater()
        self._reader = self._create_reader()
        
    def _create_updater(self):
        outer = self
        class _Updater(SynchronizedMapUpdater):
            __slots__ = ()
            def get(self, key: Any, default = None) -> Any:
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return outer._map.get(key, default)
            def update(self, key: Any, value: Any) -> None:
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        outer._map[key] = value
            def remove(self, key: Any, default = None) -> Any:
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return outer._map.pop(key, default)
            def __getitem__(self, key: Any):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return outer._map[key]  
            def __reduce__(self):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return (_create_synchronized_map_updater, (outer._lock, outer._map))
                    else:
                        raise RuntimeError("map is cleared")
        return _Updater()

    def _create_reader(self):
        outer = self
        class _Reader(SynchronizedMapReader):
            __slots__ = ()
            def get(self, key: Any, default = None) -> Any:
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return outer._map.get(key, default)
                    else:
                        raise RuntimeError("map is cleared")
            
            def __getitem__(self, key: Any):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return outer._map[key]
            
            def __reduce__(self):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return (_create_synchronized_map_reader, (outer._lock, outer._map))
                    else:
                        raise RuntimeError("map is cleared")

        return _Reader()
    
    @property
    def updater(self):
        return self._updater
    
    @property
    def reader(self):
        return self._reader
    
    def copy_map_without_usage_state_check(self) -> dict:
        with self._lock:
            if self._map is not None:
                return dict(self._map)
            else:
                raise RuntimeError("map is cleared")
    
    def clear_map_unsafe(self) -> None:
        if self._map is not None:
            self._map.clear()
            self._map = None
    
    def __reduce__(self):
        return (SynchronizedMap, (self._lock, self._map))


def _create_synchronized_map_updater(
        lock_: threading.Lock,
        map_: dict | DictProxy
) -> SynchronizedMapUpdater:
    return SynchronizedMap(lock_, map_).updater

def _create_synchronized_map_reader(
        lock_: threading.Lock,
        map_: dict | DictProxy
) -> SynchronizedMapReader:    
    return SynchronizedMap(lock_, map_).reader

