from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import date, datetime, timedelta
from ewoxcore.monitoring.models.log_event import LogEvent


class LogEvents():
    def __init__(self) -> None:
        self.events:List[LogEvent] = []
