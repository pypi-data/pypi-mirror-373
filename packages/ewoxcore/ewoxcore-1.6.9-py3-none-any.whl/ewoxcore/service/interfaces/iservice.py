from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar('T')


class IService(ABC):
    @abstractmethod
    async def on_start(self, get_service:Callable[[Type[T]], T]) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def on_stop(self) -> None:       
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def setup(self, get_service:Callable[[Type[T]], T]):
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def stop(self):
        raise NotImplementedError("Implement inhereted method")
