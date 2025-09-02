from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod
from ewoxcore.service.interfaces.iservice_collection import IServiceCollection
from ewoxcore.service.interfaces.istartup import IStartup

T = TypeVar('T')


class IStartupInternal(IStartup, ABC):
    @abstractmethod
    def configure_defaults(self, service:IServiceCollection, get_service:Callable[[Type[T]], T]) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def on_start(self) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def on_stop(self) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def dispose(self) -> None:
        raise NotImplementedError("Implement inhereted method")
