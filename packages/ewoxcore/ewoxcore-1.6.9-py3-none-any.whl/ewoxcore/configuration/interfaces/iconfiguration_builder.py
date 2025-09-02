from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod
from ewoxcore.configuration.configuration import Configuration

T = TypeVar('T')
C = TypeVar('C')


class IConfigurationBuilder(ABC):
    @abstractmethod
    def add_json_file(self, path:str) -> T:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def build(self) -> Configuration:
        raise NotImplementedError("Implement inhereted method")
