from typing import Any, List, Dict, Text, Optional, Tuple, Union
from ewoxcore.items.property_item import PropertyItem
from ewoxcore.items.item_constants import PropertyItemType
from ewoxcore.utils.url_util import UrlUtil
from ewoxcore.utils.uuid_util import UUIDUtil
from ewoxcore.utils.date_time_util import DatetimeUtil
from ewoxcore.utils.string_util import StringUtil
from ewoxcore.utils.number_util import NumberUtil
from ewoxcore.utils.dictionary_util import DictionaryUtil
from ewoxcore.utils.boolean_util import BooleanUtil


class PropertyItemAdapter():
    @staticmethod
    def convert(model:Any) -> List[PropertyItem]:
        model_dict:Dict = DictionaryUtil.convert(model)

        props:List[PropertyItem] = []
        for key, value in model_dict.items():
            if ((isinstance(value, list)) | (isinstance(value, dict))):
                continue

            value_str:str = str(value) if (value is not None) else ""

            prop:PropertyItem = PropertyItem()
            prop.name = key
            prop.value = value_str if (value is not None) else ""
            prop.type = PropertyItemAdapter.get_property_type(value_str)
            props.append(prop)

        return props


    @staticmethod
    def get_property_type(val:str) -> int:
        if (val is None):
            return int(PropertyItemType.TYPE_STRING)
        if (NumberUtil.is_integer(val)):
            return int(PropertyItemType.TYPE_INT)
        elif (NumberUtil.is_float(val)):
            return int(PropertyItemType.TYPE_FLOAT)
        elif (BooleanUtil.is_bool(val)):
            return int(PropertyItemType.TYPE_BOOLEAN)
        elif (UrlUtil.is_url(val)):
            return int(PropertyItemType.TYPE_URL)
        elif (UUIDUtil.is_valid(val)):
            return int(PropertyItemType.TYPE_GUID)
        elif (DatetimeUtil.is_time(val)):
            return int(PropertyItemType.TYPE_TIME)
        elif (DatetimeUtil.is_date(val)):
            return int(PropertyItemType.TYPE_DATETIME)
        elif (StringUtil.is_email(val)):
            return int(PropertyItemType.TYPE_EMAIL)

        return int(PropertyItemType.TYPE_STRING)
