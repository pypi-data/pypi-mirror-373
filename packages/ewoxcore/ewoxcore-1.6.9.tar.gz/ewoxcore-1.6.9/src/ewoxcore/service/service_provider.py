from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from ewoxcore.service.interfaces.iservice_provider import IServiceProvider

T = TypeVar('T')


class ServiceProvider(IServiceProvider):
    def __init__(self) -> None:
        self._func:Callable[[T], T] = None

    
    def add_service(self, func:Callable[[T], T]) -> None:
        self._func = func


    def get_service(self, type:T) -> T:
        return self._func(type)
