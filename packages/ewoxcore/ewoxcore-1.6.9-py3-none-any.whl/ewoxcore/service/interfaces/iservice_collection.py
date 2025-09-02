from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod
from ewoxcore.service.interfaces.iservice_provider import IServiceProvider

T = TypeVar('T')
C = TypeVar('C')


class IServiceCollection(ABC):
    @abstractmethod
    def add_setting(self, type:T, impl:C) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_singleton(self, type:T, impl:C) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_transient(self, type:T, impl:C) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def build_service(self) -> IServiceProvider:
        raise NotImplementedError("Implement inhereted method")
