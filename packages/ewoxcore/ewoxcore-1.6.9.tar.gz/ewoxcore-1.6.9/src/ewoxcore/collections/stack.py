from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union
from queue import LifoQueue
import threading
import copy


class Stack():
    def __init__(self, max_size:int=0) -> None:
        self._collection:LifoQueue = LifoQueue(maxsize=max_size)
        self._lock = threading.Lock()


    def get_length(self) -> int:
        return self._collection.qsize()


    def push(self, item:Any) -> None:
        with self._lock:
            self._collection.put(item)


    def pop(self, wait:bool=False) -> Optional[Any]:
        with self._lock:
            if (self._collection.empty()):
                return None
            return self._collection.get() if (wait) else self._collection.get_nowait()
