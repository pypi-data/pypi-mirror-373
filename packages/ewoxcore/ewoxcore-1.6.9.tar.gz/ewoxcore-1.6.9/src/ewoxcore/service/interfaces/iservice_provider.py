from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')


class IServiceProvider(ABC):
    @abstractmethod
    def get_service(self, type:T) -> T:
        raise NotImplementedError("Implement inhereted method")
