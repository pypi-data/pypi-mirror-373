from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta, timezone


class MonitoringEvent():
    def __init__(self, service_id:str="", serivce_name:str="", event_name:str="", event_data:str="") -> None:
      self.service_id:str = service_id
      self.serivce_name:str = serivce_name
      self.event_name:str = event_name
      self.event_data:str = event_data
      self.created_at:datetime = datetime.now(timezone.utc)
