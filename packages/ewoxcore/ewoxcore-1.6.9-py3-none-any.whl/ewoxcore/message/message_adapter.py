from typing import Any, List, Dict, Text, Optional, Tuple, Union
from datetime import datetime, timezone
from ewoxcore.message.message_args import MessageArgs

class MessageAdapter():

    @staticmethod
    def parse(data:Dict[str, Any]) -> MessageArgs:

        args:MessageArgs = MessageArgs(
            data=data.get("data", ""),
            command=data.get("command", ""),
            correlation_id=data.get("correlationId", ""),
            service_name=data.get("serviceName", ""),
            server_name=data.get("serverName", ""),
            send_at=data.get("sendAt", None),
        )

        return args
