from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type

def Serializable(cls):
    class_name = cls.__name__
    orig_init = cls.__init__

    def __init__(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.__type = class_name

    cls.__init__ = __init__
    return cls