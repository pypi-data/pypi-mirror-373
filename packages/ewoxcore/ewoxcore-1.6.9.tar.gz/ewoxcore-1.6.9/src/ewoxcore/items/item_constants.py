from enum import IntEnum


class ItemConstants():
    NAME = "Name"
    NAME_LOWER = "name"
    GROUP = "Group"
    GROUPS = "Groups"
    NUM_ROWS = "NumRows"
    INTERCHANGE = "Interchange"
    INTERCHANGE_NAMES = "InterchangeNames"


class ItemTypes(IntEnum):
    NOTDEFINED = 0
    PAGE = 100
    PAGESECTION = 101
    PROPERTY = 102
    IMAGE = 103
    VIDEO = 104
    LINK = 105
    COLORSTYLE = 106
    CONTENT = 107
    CONTENT_LIST = 108
    CONTENT_PROPERTIES = 109
    IMAGE_LIST = 110
    VIDEO_LIST = 111
    EXIF = 112
    SITE = 113
    STYLE = 114
    PAGE_SECTIONS = 115
    GROUP = 116
    GROUPS = 117
    COMPONENTS = 118
    SUBJECT = 119
    OBSERVER = 120
    GRAPH = 121
    GRAPH_NODE = 122
    GRAPH_NODE_STEP = 123
    COLLECTION = 124
    COLLECTIONS = 125
    COLLECTION_SUBJECT = 126
    OBSERVER_SUBJECT = 127
    NOTIFICATION_PREFERENCE = 128 # For collection/subject
    COLLECTION_SUBJECT_SCORE = 129
    GRAPH_NODE_COLLECTION_STEP = 130
    INTERMEDIATE = 131
    NOTIFICATION_SUBJECT_PREFERENCE = 132
    NOTIFICATION_SUBJECT_PREFERENCES = 133
    ACTION = 134
    COMMAND_SETTINGS = 135
    COMMAND_DATA = 136
    COMMAND_INPUT = 137
    COMMAND_OUTPUT = 138
    COMMAND = 139
    COLLECTION_SUBJECT_SCORE_WEEK = 140
    APP_MESSAGE = 141
    SITE_MESSAGE = 142
    GOAL = 143
    ENTITY = 144
#    GRAPH_NODE_ACTION_STEP = 137

    def to_string(self, lowerTitle:bool = False):
        s:str = str(self.name)
        if (lowerTitle):
            s = s.lower().title().replace("_","")
        return s


class PropertyItemType(IntEnum):
    TYPE_STRING = 0
    TYPE_BOOLEAN = 1
    TYPE_INT = 2
    TYPE_UINT = 3
    TYPE_NUMBER = 4
    TYPE_COLOR = 5
    TYPE_DATETIME = 6
    TYPE_TEXTAREA = 7
    TYPE_EMPTY = 8 # Used for formatting the UI and therefore leave an empty space
    TYPE_LIST =  9 # List of string
    TYPE_DOUBLE = 10
    TYPE_GUID = 11
    TYPE_FLOAT = 12
    TYPE_EMAIL = 13
    TYPE_PHONE = 14
    TYPE_DATE = 15
    TYPE_URL = 16
    TYPE_STRING_LIST = 17
    TYPE_TIME = 18
    TYPE_PASSWORD = 19
    TYPE_PIXELS = 20
    TYPE_PERCENT = 21
    TYPE_HTML = 22
    TYPE_PATH = 23
    TYPE_BOOLEAN_CHECKBOX = 24
    TYPE_TEXTAREA_STRING = 25
    TYPE_STRING_BASE64 = 100
    TYPE_TEXTAREA_BASE64 = 101

    def to_string(self, lowerTitle:bool = False):
        s:str = str(self.name)
        if (lowerTitle):
            s = s.lower().title().replace("_","")
        return s


class LevelValidatedType(IntEnum):
    LEVEL_NONE = 0     # Content is not validated


class PropertySelectorType(IntEnum):
    STANDARD = 0
    AUTOCOMPLETE = 1