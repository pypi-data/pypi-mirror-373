from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod
from ewoxcore.monitoring.models.log_event import LogEvent

T = TypeVar('T')


class ILogger(ABC):
    @abstractmethod
    def setup(self) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def info(self, message:str, *args, **kwargs) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def warning(self, message:str, *args) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def error(self, message:str, *args) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def debug(self, message:str, *args) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def info_ext(self, event:LogEvent) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def warning_ext(self, event:LogEvent) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def error_ext(self, event:LogEvent) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def debug_ext(self, event:LogEvent) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def log_scoped(self, level: str, message: str, args: Optional[T] = None) -> None:
        raise NotImplementedError("Implement inhereted method")
