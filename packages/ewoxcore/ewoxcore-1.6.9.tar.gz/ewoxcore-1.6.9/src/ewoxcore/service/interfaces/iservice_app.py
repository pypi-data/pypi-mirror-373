from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')


class IServiceApp(ABC):
    @abstractmethod
    async def on_start(self) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def on_stop(self) -> None:
        raise NotImplementedError("Implement inhereted method")
