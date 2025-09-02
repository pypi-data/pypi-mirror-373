from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union
from abc import ABC, abstractmethod
from ewoxcore.items.item import Item


class IMemoryHandle(ABC):
    @abstractmethod
    def add(self, variable:str, inner_state:str) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def remove(self, variable:str, inner_state:str) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get_inner_states(self, variable:str) -> List[str]:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def contains(self, variable:str) -> bool:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def check(self, variable:str, inner_state:str) -> bool:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_item(self, variable:str, item:Item) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get_items_keys(self) -> List[str]:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get_items(self, variable:str) -> List[Item]:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError("Implement inhereted method")
