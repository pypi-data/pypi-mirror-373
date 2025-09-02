from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
import json
from queue import Queue
from types import SimpleNamespace
from ewoxcore.utils.class_util import ClassUtil


T = TypeVar("T")


class Configuration():
    def __init__(self) -> None:
        self._settings:List[Dict] = []


    def add(self, settings:Dict) -> Dict:
        if (isinstance(settings, Dict)):
            self._settings.append(settings)


    def _get_dict(self, data:Dict, keys_stack:Queue) -> Optional[Dict]:
        if (keys_stack.empty()):
            return data

        key:str = keys_stack.get()
        if (key in data):
            sub_dict:Dict = data[key]
            return self._get_dict(sub_dict, keys_stack)


    def _get_section_dict(self, key:str) -> Optional[Dict]:
        keys:List[str] = key.split(":")

        for setting in self._settings:
            keys_stack:Queue = Queue()
            for k in keys:
                keys_stack.put(k)

            section:Dict = self._get_dict(setting, keys_stack)
            if (section):
                return section

        return None


    def get_section(self, class_type:T, key:str) -> Optional[T]:
        dict_obj:Dict = self._get_section_dict(key)
        if (dict_obj is None):
            return None

        json_str = json.dumps(dict_obj)
        json_obj = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))       
        class_d:T = ClassUtil.merge(class_type(), json_obj)

        return class_d
