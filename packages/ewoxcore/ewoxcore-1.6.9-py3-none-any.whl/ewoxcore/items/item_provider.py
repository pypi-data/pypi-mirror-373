from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable
from datetime import date, datetime, timedelta
import copy
from dateutil.parser import parse
from ewoxcore.items.item_constants import PropertyItemType
from ewoxcore.items.key_value_pair import KeyValuePair
from ewoxcore.items.item_base import ItemBase
from ewoxcore.items.property_item import PropertyItem
from ewoxcore.items.item import Item
from ewoxcore.utils.uuid_util import UUIDUtil


class ItemProvider():
    @staticmethod
    def is_root(item:Item) -> bool:
        if item.parentItemId == "":
            return True
        else:
            return False


    @staticmethod
    def change_id(item:Item, itemId:str):
        item.itemId = itemId


    @staticmethod
    def get_property_item(item:Item, name:str, search_child:bool=False) -> Optional[PropertyItem]:
        if (item is None):
            return None

        prop:PropertyItem = None
        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    prop = p
                    break

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_item(child, name, search_child)
                if (prop is not None):
                    return prop

        return prop


    @staticmethod
    def get_property_item_by_id(item:Item, id:str, search_child:bool=False) -> PropertyItem:
        if (item is None):
            return None

        prop:PropertyItem = None
        for p in item.properties:
            if (p.itemId == id):
                return p

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_item_by_id(child, id, search_child)
                if (prop is not None):
                    return prop

        return prop


    @staticmethod
    def add_property(item:Item, prop:PropertyItem) -> None:
        if (item is None):
            return

        prop.idx = len(item.properties) + 1
        item.properties.append(prop)


    @staticmethod
    def add_properties(item:Item, props:List[PropertyItem]) -> None:
        if (item is None):
            return

        for prop in props:
            prop.idx = len(item.properties) + 1
            item.properties.append(prop)


    @staticmethod
    def get_subitem(item:Item, name:str, search_child:bool=False, match_item_type:int=None) -> ItemBase:
        if (item is None):
            return None

        i:ItemBase = None
        for si in item.subItems:
            if (si.name == name):
                if (match_item_type is not None):
                    if ((si.name == name) & (si.itemType == match_item_type)):
                        return si
                else:
                    return si
            if (search_child):
                i = ItemProvider.get_subitem(si, name, search_child)
                if (i is not None):
                    return i

        return i


    @staticmethod
    def get_subitem_by_id(item:Item, itemId:str, search_child:bool=False) -> ItemBase:
        if (item is None):
            return None

        i:ItemBase = None
        for si in item.subItems:
            if (si.itemId == itemId):
                return si
            if (search_child):
                i = ItemProvider.get_subitem_by_id(si, itemId, search_child)
                if (i is not None):
                    return i

        return i


    @staticmethod
    def get_subitem_by_type(item:Item, item_type:int, search_child:bool=False) -> ItemBase:
        i:ItemBase = None
        if (item is None):
            return None

        for si in item.subItems:
            if (si.itemType == item_type):
                return si
            if (search_child):
                i = ItemProvider.get_subitem_by_type(si, item_type, search_child)
                if (i is not None):
                    return i

        return i


    @staticmethod
    def remove_subitem(item:Item, item_id:str, search_child:bool=False) -> int:
        del_index:int = -1
        for index, si in enumerate(item.subItems):
            if (si.itemId == item_id):
                del_index = index
                break

            if (search_child):
                del_index = ItemProvider.remove_subitem(si, item_id, search_child)
                if (del_index != -1):
                    del item.subItems[del_index]
                    return del_index

        if (del_index != -1):
            del item.subItems[del_index]
            return -1

        return del_index


    @staticmethod
    def add_subitem(item:Item, sub_item:ItemBase) -> None:
        if (sub_item is None):
            return
        sub_item.parentItemId = item.itemId
        item.subItems.append(sub_item)


    @staticmethod
    def set_property_value(item:Item, name:str, value:str) -> None:
        if (item is None):
            return

        for p in item.properties:
            if (p.name == name):
                p.value = str(value)


    @staticmethod
    def get_property_value_string(item:Item, name:str, default_val:str="", search_child:bool=False) -> str:
        if (item is None):
            return default_val

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    return str(p.value)

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_string(child, name, default_val, search_child)
                if (prop is not None):
                    return prop

        return default_val


    @staticmethod
    def get_property_value_uuid(item:Item, name:str, search_child:bool=False) -> str:
        if (item is None):
            return ""

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    value:str = str(p.value)
                    return value if (UUIDUtil.is_valid(value)) else ""

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_uuid(child, name, search_child)
                if (prop is not None):
                    return prop

        return ""


    @staticmethod
    def get_property_value_int(item:Item, name:str, default_val:int=0, search_child:bool=False) -> int:
        if (item is None):
            return default_val

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    if (p.value == ""):
                        return default_val
                    return int(p.value)

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_int(child, name, default_val, search_child)
                if (prop is not None):
                    return prop

        return default_val


    @staticmethod
    def get_property_value_float(item:Item, name:str, default_val:float=0, search_child:bool=False) -> float:
        if (item is None):
            return default_val

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    if (p.value == ""):
                        return default_val
                    return float(p.value)

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_float(child, name, default_val, search_child)
                if (prop is not None):
                    return prop

        return default_val


    @staticmethod
    def get_property_value_datatime(item:Item, name:str, search_child:bool=False) -> datetime:
        """ DEPRECATED. Keep it for backward compatiability. """
        if (item is None):
            return None

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    if (p.value):
                        return parse(p.value)
                    else:
                        return None

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_datatime(child, name, search_child)
                if (prop is not None):
                    return prop

        return None


    @staticmethod
    def get_property_value_datetime(item:Item, name:str, search_child:bool=False) -> datetime:
        if (item is None):
            return None

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    if (p.value):
                        return parse(p.value)
                    else:
                        return None

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_datetime(child, name, search_child)
                if (prop is not None):
                    return prop

        return None


    @staticmethod
    def get_property_value_date(item:Item, name:str, search_child:bool=False) -> date:
        if (item is None):
            return None

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    if (p.value):
                        return parse(p.value).date()
                    else:
                        return None

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_date(child, name, search_child)
                if (prop is not None):
                    return prop

        return None


    @staticmethod
    def get_property_value_bool(item:Item, name:str, default_value:bool=False, search_child:bool=False) -> bool:
        if (item is None):
            return default_value

        for p in item.properties:
            if (hasattr(p, "name")):
                if (p.name == name):
                    return True if (str(p.value).lower() == "true") else False

        if (search_child):
            for child in item.subItems:
                prop = ItemProvider.get_property_value_bool(child, name, search_child)
                if (prop is not None):
                    return prop

        return False


    @staticmethod
    def create_property(name:str, label:str="", value:str="", type:int=0, is_editable:bool=True) -> PropertyItem:
        prop = PropertyItem()
        prop.name = str(name)
        prop.label = str(label)
        prop.value = str(value)
        prop.type = int(type)
        prop.isEditable = bool(is_editable)
        return prop


    @staticmethod
    def merge(old:Item, new:Item, by_name:bool=False, exclude_locked:bool=False) -> Item:
        """ Merge the new item properties into the old item. """
        if (new is None):
            return old

        for new_prop in new.properties:
            if (new_prop.value == ""):
                continue

            old_prop:PropertyItem = ItemProvider.get_property_item(old, new_prop.name)
            if (old_prop is not None):
                if (exclude_locked == True):
                    if (old_prop.isLocked == False):
                        old_prop.value = new_prop.value
                else:
                    old_prop.value = new_prop.value
            else:
                if (new_prop.label == ""):
                    new_prop.label = new_prop.name.title()
                ItemProvider.add_property(old, new_prop)

        if (by_name):
            for subitem in new.subItems:
                old_subitem:Item = ItemProvider.get_subitem(
                    item=old, 
                    name=subitem.name, 
                    search_child=False, 
                    match_item_type=subitem.itemType)
                if (old_subitem is None):
                    old.subItems.append(subitem)
                else:
                    ItemProvider.merge(old_subitem, subitem, by_name, exclude_locked=exclude_locked)
        else:
            # This is needed for situations where we have multiple items 
            # with the same name and itemType at the same level.
            for index, subitem in enumerate(new.subItems):
                if (index >= len(old.subItems)):
                    old.subItems.append(subitem)
                else:
                    old_subitem:Item = old.subItems[index]
                    ItemProvider.merge(old_subitem, subitem, by_name, exclude_locked=exclude_locked)

        return old


    @staticmethod
    def merge_props(old:Item, new:Item, include_new:bool=False) -> Item:
        """ Merge the new item properties into the old item (only existing props in old item if include_new = False)."""
        if (new is None):
            return old

        for new_prop in new.properties:
            if (new_prop.value):
                old_prop:PropertyItem = ItemProvider.get_property_item(old, new_prop.name)
                if (old_prop):
                    old_prop.value = new_prop.value
                elif (include_new):
                    if (new_prop.label == ""):
                        new_prop.label = new_prop.name.title()
                    ItemProvider.add_property(old, new_prop)

        return old


    @staticmethod
    def add_missing_props(item:Item, template:Item) -> None:
        if (template is None):
            return None

        for new_prop in template.properties:
            prop:PropertyItem = ItemProvider.get_property_item(item, new_prop.name)
            if (prop is None):
                ItemProvider.add_property(item, new_prop)


    @staticmethod
    def remove_props(item:Item, template:Item) -> None:
        if ((item is None) | (template is None)):
            return None

        for exist_prop in item.properties:
            prop:PropertyItem = ItemProvider.get_property_item(template, exist_prop.name)
            if (prop is None):
                ItemProvider.remove_property(item, exist_prop.name)


    @staticmethod
    def remove_property(item:Item, prop_name:str) -> int:
        del_index:int = -1
        for index, pi in enumerate(item.properties):
            if (pi.name == prop_name):
                del_index = index
                break

        if (del_index != -1):
            del item.properties[del_index]
            return -1

        return del_index


    @staticmethod
    def clone(item:Item, change_id:bool=True) -> Item:
        if (item is None):
            return None

        new_item:Item = Item()
        if (change_id == False):
            new_item.change_id(item.itemId)

        new_item.parentItemId = item.parentItemId
        new_item.name = item.name
        new_item.label = item.label
        new_item.itemType = item.itemType
        new_item.appType = item.appType
        if (hasattr(item, "isHidden") == False):
            setattr(item, "isHidden", False)
        else:
            new_item.isHidden = item.isHidden

        new_item.properties = copy.deepcopy(item.properties)
        new_item.subItems = ItemProvider.clone_items(item.subItems)
        new_item.relations  = copy.deepcopy(item.relations)
        new_item.externalId = item.externalId

        return new_item


    @staticmethod
    def clone_items(items:List[Item], change_id:bool=True) -> List[Item]:
        new_items:List[Item] = []
        for item in items:
            new_item:Item = ItemProvider.clone(item, change_id)
            new_items.append(new_item)

        return new_items


    @staticmethod
    def clone_property(prop:PropertyItem) -> PropertyItem:
        new = PropertyItem()
        new.name = prop.name
        new.label = prop.label
        new.itemType = prop.itemType
        new.appType = prop.appType
        new.idx = prop.idx
        new.type = prop.type
        new.value = prop.value
        new.levelValidated = prop.levelValidated
        new.isRequired = prop.isRequired
        new.labelAfter = prop.labelAfter
        new.tooltip = prop.tooltip
        new.help = prop.help
        new.isEditable = prop.isEditable
        new.isEditableDisplayable = prop.isEditableDisplayable
        new.fillRow = prop.fillRow
        new.placeholderName = prop.placeholderName
        new.isLocked = prop.isLocked
        new.selector = prop.selector

        return new


    @staticmethod
    def is_valid(item:Item) -> bool:
        if (item is None):
            return False

        for prop in item.properties:
            if ((prop.isRequired) & (prop.value == "")):
                return False
        return True


    @staticmethod
    def add_relation(item:Item, kv:KeyValuePair) -> None:
        item.relations.append(kv)


    @staticmethod
    def add_relation(item:Item, key:str, value:str) -> None:
        item.relations.append(KeyValuePair(key, value))


    @staticmethod
    def has_relation(item:Item, key:str) -> bool:
        for kv in item.relations:
            if (kv.key == key):
                return True
        return False


    @staticmethod
    def get_relation(item:Item, key:str) -> Optional[KeyValuePair]:
        for kv in item.relations:
            if (kv.key == key):
                return kv
        return None


    @staticmethod
    def get_item_by_relation(item:Item, key:str, value:str) -> Optional[Item]:
        for subItem in item.subItems:
            kv:KeyValuePair = ItemProvider.get_relation(subItem, key, value)
            if (kv):
                return subItem
        return None


    @staticmethod
    def get_item_by_relation(item:Item, key_value:KeyValuePair) -> Optional[Item]:
        return ItemProvider.get_item_by_relation(item, key_value.key, key_value.value)


    @staticmethod
    def get_subitems(item:Item, name:str, search_child:bool=False, match_item_type:int=None) -> List[ItemBase]:
        items:List[ItemBase] = []
        if (item is None):
            return []

        for si in item.subItems:
            if (si.name == name):
                if (match_item_type is not None):
                    if ((si.name == name) & (si.itemType == match_item_type)):
                        items.append(si)
                else:
                    items.append(si)
            if (search_child):
                for si in item.subItems:
                    child_items:List[ItemBase] = ItemProvider.get_subitems(si, name, search_child, match_item_type)
                    items =  items + child_items

        return items


    @staticmethod
    def is_property_number(prop:PropertyItem) -> bool:
        if ((prop.type == int(PropertyItemType.TYPE_INT)) |
            (prop.type == int(PropertyItemType.TYPE_UINT)) | 
            (prop.type == int(PropertyItemType.TYPE_FLOAT)) |
            (prop.type == int(PropertyItemType.TYPE_DOUBLE)) |
            (prop.type == int(PropertyItemType.TYPE_NUMBER)) |
            (prop.type == int(PropertyItemType.TYPE_PERCENT))):
            return True
        return False


if __name__ == "__main__":
    i1 = Item()
    i1.name = "i1"

    i1_1 = Item()
    i1_1.name = "i1_1"
    i1.add_subitem(i1_1)

    i1_2 = Item()
    i1_2.name = "i1_2"
    i1.add_subitem(i1_2)

    i2_2 = Item()
    i2_2.name = "i2_2"
    i1_2.add_subitem(i2_2)

    i1_3 = Item()
    i1_3.name = "i1_3"
    i1.add_subitem(i1_3)

    ItemProvider.remove_subitem(i1, i2_2.itemId, search_child=True)
