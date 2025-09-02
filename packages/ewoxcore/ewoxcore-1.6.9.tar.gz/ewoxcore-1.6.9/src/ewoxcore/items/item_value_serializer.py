from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable
import base64


class ItemValueSerializer:   
    @staticmethod
    def serialize_base64(value:str) -> str:
        val_serialized:str = base64.standard_b64encode(value.encode()).decode()
        return val_serialized


    @staticmethod
    def deserialize_base64(value:str) -> str:
        val_deserialized:str = base64.standard_b64decode(value).decode()
        return val_deserialized


    @staticmethod
    def serialize(value:str) -> str:
        value = value.replace("'", "(!!)")
        vals:List[str] = value.split('\\')
        if (len(vals) > 1):
            value = vals[0] + "(|)" + vals[1]

        return value


    @staticmethod
    def deserialize(value:str) -> str:
        value = value.replace("(!!)", "'")
        return value.replace("(|)", "\\")
