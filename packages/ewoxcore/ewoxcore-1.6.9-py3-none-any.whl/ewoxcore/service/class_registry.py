from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta


class ClassRegistry():
    _class_types:Dict[str, Any] = dict()


    @staticmethod
    def register(name:str, cls:Type[Any]) -> None:
        """ Register a class with a name. """
        if (name in ClassRegistry._class_types):
            return

        ClassRegistry._class_types[name] = cls


    @staticmethod
    def get(name:str) -> Type[Any]:
        """ Get a class by name. """
        if (name not in ClassRegistry._class_types):
            raise ValueError(f"Class with name '{name}' is not registered.")

        cls = ClassRegistry._class_types[name]
        if (not isinstance(cls, type)):
            raise TypeError(f"Registered handler for '{name}' is not a class.") 

        return cls


    
