from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import date, time, datetime, timedelta, timezone
from ewoxcore.utils.date_time_util import DatetimeUtil


class LogEvent():
    def __init__(self, correlation_id:str="", user_id:str=None, company_id:str=None, 
                 log_level:int=1, message:str="", event_name:str="", event_type:str="", 
#                 data_class:str ="", data:str="", is_encoded:bool=False, created_at:datetime=datetime.now(tz=timezone.utc)()) -> None:
                 data_class:str ="", data:str="", is_encoded:bool=False, created_at:datetime=datetime.now(tz=timezone.utc)) -> None:
        self.correlationId:str = correlation_id
        self.userId:str = user_id
        self.companyId:str = company_id
        self.logLevel:int = log_level
        self.message:str = str(message)
        self.eventName:str = event_name
        self.eventType:str = event_type
        self.dataClass:str = data_class
        self.data:str = data
        self.isEncoded:bool = is_encoded # Base64 encoded data.
        self.createdAt:datetime = created_at
