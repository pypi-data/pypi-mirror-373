from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union
from collections import deque


class FIFOQueue():
    def __init__(self):
        self._items = deque()


    def append(self, item):
        self._items.append(item)


    def pop(self):
        try:
            return self._items.popleft()
        except IndexError:
            pass


    def __len__(self):
        return len(self._items)


    def __contains__(self, item):
        return item in self._items


    def __iter__(self):
        yield from self._items


    def __reversed__(self):
        yield from reversed(self._items)


    def __repr__(self):
        return f"Queue({list(self._items)})"