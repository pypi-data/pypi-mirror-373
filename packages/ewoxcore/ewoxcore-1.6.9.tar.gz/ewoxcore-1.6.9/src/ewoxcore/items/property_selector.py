from typing import Any, List, Dict, Text, Optional, Tuple, Union
from ewoxcore.items.item_constants import PropertySelectorType


class PropertySelector:
    def __init__(self, name:str="", type:int=0, data_type:int=int(PropertySelectorType.STANDARD)):
        self.name:str = name
        self.dataSource:str = ""
#        self.buttonItem:Item
        self.type:int = type # Used as client type
        self.dataType:int = data_type
        self.keys:List[str] = []
