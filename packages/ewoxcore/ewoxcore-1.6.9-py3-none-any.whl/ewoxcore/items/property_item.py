#from items.property_selector import PropertySelector
#from items.item_base import ItemBase
from .item_base import ItemBase
from .property_selector import PropertySelector
from .item_constants import LevelValidatedType
from .item_constants import PropertyItemType
from .item_constants import ItemTypes

class PropertyItem(ItemBase):
    def __init__(self, name:str="", type:int=int(PropertyItemType.TYPE_STRING), value:str="", 
                 label:str="", is_required:bool=False, is_editable:bool=True, is_editable_displayable:bool=False,
                 selector:PropertySelector=None, tooltip:str="", parentItemId:str=""):
        super().__init__(name, label, parentItemId)
        self.idx:int = 0
        self.type:int = type
        self.value:str = value
        self.levelValidated:int = int(LevelValidatedType.LEVEL_NONE)
        self.isRequired:bool = is_required
        self.labelAfter:str = ""
        self.tooltip:str = tooltip
        self.help:str = ""
        self.isEditable:bool = is_editable
        self.isEditableDisplayable:bool = is_editable_displayable
        self.fillRow:bool = False
        self.placeholderName:str = ""
        self.isLocked:bool = False
        self.selector:PropertySelector = selector
        self.hasChanged:bool = False
        self.itemType = int(ItemTypes.PROPERTY)


    def clone(self):
        item = PropertyItem()
        item.parentItemId = self.parentItemId
        item.name = self.name
        item.itemType = self.itemType
        item.appType = self.appType
        item.idx = self.idx
        item.type = self.type
        item.value = self.value
        item.levelValidated = self.levelValidated
        item.isRequired = self.isRequired
        item.label = self.label
        item.labelAfter = self.labelAfter
        item.tooltip = self.tooltip
        item.help = self.help
        item.isEditable = self.isEditable
        item.fillRow = self.fillRow
        item.isEditableDisplayable = self.isEditableDisplayable
        item.placeholderName = self.placeholderName
        item.isLocked = self.isLocked

        return item
