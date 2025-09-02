from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod

class IMessageConsumer(ABC):
    @abstractmethod
    async def on_consume(self, command:str, correlation_id:str, json64:str, service_name:str="") -> None:
        """ Handle the consumed message. """
        raise NotImplementedError("Implement inhereted method")
