from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from abc import ABC, abstractmethod


class ILocalizer(ABC):
    @abstractmethod
    def register(self, language_code:str, language_two_letter:str) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def setup(self, path:str="./data/translations", default_language:str="en-GB") -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get(self, key:str, language_code:str="en-GB") -> str:
        raise NotImplementedError("Implement inhereted method")
