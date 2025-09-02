from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod
from ewoxcore.service.interfaces.iservice_collection import IServiceCollection

T = TypeVar('T')


class IStartup(ABC):
    @abstractmethod
    def configure_services(self, service:IServiceCollection, get_service:Callable[[Type[T]], T], use_unittest:bool=False) -> None:
        raise NotImplementedError("Implement inhereted method")


#    @abstractmethod
#    def setup(self, get_service:Callable[[Type[T]], T]) -> None:
#        """ Setup is being called after all service configurations. """
#        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def setup_async(self, get_service:Callable[[Type[T]], T]) -> None:
        """ Setup is being called after all service configurations. """
        pass