from typing import Any, List, Dict, Text, Optional, Tuple, Union
from datetime import datetime, timezone
import uuid

class ServiceIdentifier():
    def __init__(self, name:str) -> None:
        self.id:str = str(uuid.uuid4())
        self.name:str = name
