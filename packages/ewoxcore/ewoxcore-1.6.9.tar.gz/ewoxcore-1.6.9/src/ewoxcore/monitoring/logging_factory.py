from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from ewoxcore.monitoring.models.log_event import LogEvent
from ewoxcore.monitoring.constants.log_level import LogLevel
from ewoxcore.utils.json_util import JsonUtil

T = TypeVar('T')


class LoggingFactory():
    @staticmethod
    def create(correlation_id:str, user_id:str, company_id:str="", log_level:int=int(LogLevel.Info), message:str="", event_name:str="", event_type:str="", args:T=None) -> LogEvent:
        data_class:str = args.__class__.__name__ if (args is not None) else ""
        data:str = JsonUtil.serializeJson64(args) if (args is not None) else ""
        event:LogEvent = LogEvent(correlation_id, user_id, company_id, log_level, message, event_name, event_type, data_class, data, is_encoded=True)

        return event
