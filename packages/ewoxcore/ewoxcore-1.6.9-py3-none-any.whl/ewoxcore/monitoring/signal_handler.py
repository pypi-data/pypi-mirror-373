from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from signal import SIGINT, SIGTERM, SIGKILL, signal
import asyncio

T = TypeVar('T')


class SignalHandler:
    __on_stop_callback:Callable[[None], None] = None

    def __init__(self) -> None:
        self.received_signal = False


    def setup(self) -> None:
        signal(SIGINT, self._on_handle)
        signal(SIGTERM, self._on_handle)
#        signal(SIGKILL, self._on_handle)


    def set_callback(self, on_stop:Callable[[None], None]) -> None:
        SignalHandler.__on_stop_callback = on_stop


    def _on_handle(self, signal:int, frame:Any) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(self._dispose())


    async def _dispose(self) -> None:
        if (self.received_signal):
            return

        self.received_signal = True
        if (SignalHandler.__on_stop_callback is not None):
            await SignalHandler.__on_stop_callback()
