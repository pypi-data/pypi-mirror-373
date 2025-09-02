from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable
from datetime import date, datetime, timedelta
from .item import Item
from ewoxcore.utils.json_util import JsonUtil


class ItemConverter():
    @staticmethod
    def convert_to_json(item:Item) -> str:
        if (item is None):
            return "{}"

        json_dict:Dict = dict()
        for prop in item.properties:
            if (prop.name):
                json_dict[prop.name] = prop.value

        json_str:str = JsonUtil.serialize(json_dict, keep_object=False)
        return json_str
