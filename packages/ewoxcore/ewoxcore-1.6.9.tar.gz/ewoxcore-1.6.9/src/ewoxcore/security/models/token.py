from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import date, time, datetime, timedelta, timezone



class Token():
    def __init__(self, user_id:str="", expire:datetime=None, data:str="", roles:List[str]=[]) -> None:
        self.userId:str = user_id
        self.expireAt:datetime = expire
        self.data:str = data
        self.roles:List[str] = roles
