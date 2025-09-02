import uuid

class ItemBase:
    def __init__(self, name:str="", label:str="", parentItemId:str=""):
        self.itemId:str = str(uuid.uuid4())
        self.parentItemId:str = parentItemId
        self.name:str = name
        self.label:str = label
        self.itemType:int = 0
        self.appType:int = 0
        
