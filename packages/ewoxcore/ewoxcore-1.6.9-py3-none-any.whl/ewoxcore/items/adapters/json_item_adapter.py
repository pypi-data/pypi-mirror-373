from typing import Any, List, Dict, Text, Optional, Tuple, Union
import json
from ewoxcore.items.adapters.property_item_adapter import PropertyItemAdapter
from ewoxcore.items.item import Item
from ewoxcore.items.property_item import PropertyItem
from ewoxcore.items.item_provider import ItemProvider
from ewoxcore.utils.json_util import JsonUtil
from ewoxcore.utils.string_util import StringUtil


class JsonItemAdapter():
    @staticmethod
    def convert(json_decoded:str, item:Item=None) -> Item:
        json_dict:Dict = json.loads(json_decoded)

        if (item is None):
            item = Item()

        provider = ItemProvider()
        for key, value in json_dict.items():
            if ((isinstance(value, list)) | (isinstance(value, dict))):
                continue
            if (value is None):
                continue

            prop_name:str = str(key).lower()
            prop:PropertyItem = provider.get_property_item(item, prop_name)
            if (prop is None):
                prop = PropertyItem()
                prop.name = prop_name
                prop.label = StringUtil.title_capitalized(str(key))
                prop.value = str(value)
                prop.type = PropertyItemAdapter.get_property_type(value)
                item.add_property(prop)
            elif (value != ""):
                prop.value = str(value)
                prop.type = PropertyItemAdapter.get_property_type(value)

            internal_prop_name:str = "_"+ str(key).lower()
            internal_prop:PropertyItem = provider.get_property_item(item, internal_prop_name)
            if (internal_prop is not None):
                internal_prop.value = str(value)

        return item


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


    @staticmethod
    def convert_to_json64(item:Item) -> str:
        json_dict:Dict = dict()
        for prop in item.properties:
            # We exclude internal properties starting with _
            if (prop.name.startswith("_") == False):
                json_dict[prop.name] = prop.value

        json_str:str = JsonUtil.serializeJson64(json_dict, keep_object=False)
        return json_str
