from typing import Any, List, Dict, Text, Optional, Tuple, Union
from datetime import datetime, timezone
import uuid

class MessageArgs():
    def __init__(self, data:str="", command:str="", correlation_id:str=None, service_name:str="", server_name:str="", send_at:datetime=datetime.now(timezone.utc)) -> None:
        self.data:str = data # The data must be encoded using JsonUtil.serializeJson64
        self.command:str = command
        self.correlationId:str = str(uuid.uuid4()) if (correlation_id is None) else correlation_id
        self.serviceName:str = service_name
        self.serverName:str = server_name
        self.sendAt:datetime = send_at
