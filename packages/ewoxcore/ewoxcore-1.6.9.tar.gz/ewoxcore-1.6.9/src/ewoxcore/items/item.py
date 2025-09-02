from typing import List
from .key_value_pair import KeyValuePair
from .item_base import ItemBase
from .property_item import PropertyItem


class Item(ItemBase):
    def __init__(self):
        super().__init__()
        self.properties:List[PropertyItem] = []
        self.subItems:List[Item] = []
        self.relations:List[KeyValuePair] = []
        self.externalId:str = ""
        self.isHidden:bool=False

    
    def is_root(self) -> bool:
        if self.parentItemId == "":
            return True
        else:
            return False


    def change_id(self, itemId:str) -> None:
        self.itemId = itemId


    def get_property_item(self, name:str) -> PropertyItem:
        prop:PropertyItem = None
        for p in self.properties:
            if (p.name == name):
                prop = p
                break

        return prop


    def add_property(self, prop:PropertyItem) -> None:
        if (prop is None):
            return

        prop.idx = len(self.properties) + 1
        self.properties.append(prop)


    def get_subitem(self, name:str) -> ItemBase:
        si:ItemBase = None
        for i in self.subItems:
            if (i.name == name):
                si = i
                break

        return si


    def add_subitem(self, item:ItemBase) -> None:
        if (item is None):
            return

        item.parentItemId = self.itemId
        self.subItems.append(item)
    

    def add_relation(self, kv:KeyValuePair) -> None:
        self.relations.append(kv)


    def add_relation(self, key:str, value:str) -> None:
        self.relations.append(KeyValuePair(key, value))
