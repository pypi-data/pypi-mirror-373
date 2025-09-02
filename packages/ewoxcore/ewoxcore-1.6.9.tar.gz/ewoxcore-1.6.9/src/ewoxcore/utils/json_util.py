from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from types import SimpleNamespace
import base64
import jsonpickle
import json
import re
from ewoxcore.utils.class_util import ClassUtil
from ewoxcore.utils.dictionary_util import DictionaryUtil

T = TypeVar("T")

"""
Use Humps for converting between snake case, camelcase and pascalcase
https://humps.readthedocs.io/en/latest/
"""
class JsonUtil:

    @staticmethod
    def serializeJson64(val, keep_object:bool=False) -> str:
        if (val is None):
            return ""
        
        # unpickable must be set to true, otherwise deserialize to an object will not work.
        json_str = jsonpickle.encode(val, unpicklable=keep_object, make_refs=False)
    
        json64:str = base64.standard_b64encode(json_str.encode()).decode()
    
        return json64


    @staticmethod
    def deserializeJson64(val:str, to_object:bool=True):
        """ Deperected, use: deserialize_json64"""
        if ((val == "") | (val is None)):
            return None
        json64 = base64.standard_b64decode(val)
        json_str = json64.decode()
        decObj = jsonpickle.decode(json_str)
        if ((to_object) and (type(decObj) == type({}))):
            decObj = JsonUtil.deserialize_object(json_str)
            return decObj

        return decObj


    @staticmethod
    def deserialize_json64(class_type:T, val:str, to_object:bool=True, force_merge:bool=False):
        if ((val == "") | (val is None)):
            return None
        json64 = base64.standard_b64decode(val)
        json_str = json64.decode()
        decObj = jsonpickle.decode(json_str)
        if ((to_object) and (type(decObj) == type({}))):
            decObj = JsonUtil.deserialize_object(json_str)
            decObj = ClassUtil.merge(class_type(), decObj)
            return decObj
        if ((to_object) and (force_merge)):
            decObj = ClassUtil.merge(class_type(), decObj)
            return decObj

        return decObj
    

    @staticmethod
    def serialize(val, keep_object:bool=False) -> str:
        if (val is None):
            return ""
        
        json_str = jsonpickle.encode(val, unpicklable=keep_object)
        
        return json_str


    @staticmethod
    def serialize_list(val) -> str:
        json_str = json.dumps(val)
        return json_str


    @staticmethod
    def deserialize_object(val:str):
        if (val == ""):
            return None
        decObj = json.loads(val, object_hook=lambda d: SimpleNamespace(**d))
        return decObj


    @staticmethod
    def deserialize_gen_object(class_type:T, val:str):
        if (val == ""):
            return None
        decObj = json.loads(val, object_hook=lambda d: SimpleNamespace(**d))       
        decObj = ClassUtil.merge(class_type(), decObj)

        return decObj


    @staticmethod
    def deserialize(val:str):
        if (val == ""):
            return None
        decObj = jsonpickle.decode(val)
        return decObj


    @staticmethod
    def write_dict(file_name:str, data:Dict):
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)


    @staticmethod
    def read_dict(file_name:str):
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data


    @staticmethod
    def write(file_name:str, model:Any):
        json_data = json.dumps(model, default=lambda o: o.__dict__, indent=4)
        with open(file_name, 'w') as outfile:
            outfile.write(json_data)


    @staticmethod
    def write_utf8(file_name:str, model:Any):
        json_data = json.dumps(model, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
        with open(file_name, 'w', encoding='utf8') as outfile:
            outfile.write(json_data)


    @staticmethod
    def write_text(file_name:str, text:str):
        with open(file_name, 'w') as outfile:
            outfile.write(text)


    @staticmethod
    def is_base64(val:str) -> bool:
        x = re.search("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$", val)
        if (x):
            return True
        return False


    @staticmethod
    def decode_json(val:str) -> str:
        json64 = base64.standard_b64decode(val)
        json_str = json64.decode()
        return json_str


    @staticmethod
    def encodeBase64(json_str:Any) -> str:
        json64:str = base64.standard_b64encode(json_str.encode()).decode()
        return json64


    @staticmethod
    def get_value(json_str:str, name:str, default:Any) -> Any:
        json_dict:Dict = json.loads(json_str)
        return DictionaryUtil.get(json_dict, name, default)
