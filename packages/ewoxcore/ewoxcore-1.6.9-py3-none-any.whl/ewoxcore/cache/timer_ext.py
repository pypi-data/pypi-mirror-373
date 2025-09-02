from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable
import time
import threading


class TimerExt(threading.Thread):
    def __init__(self, callback, interval_seconds:int, activate_immediately:bool):
        super().__init__()
        self.callback = callback
        self._interval_seconds = interval_seconds
        self._running:bool = True
        self._active:bool = True if (activate_immediately) else False


    def run(self):
        while self._running:
            if self._active:
                for x in range(0,self._interval_seconds):
                    if self._active:
                        time.sleep(1)
                self.callback()
            else:
                time.sleep(float(0.1))


    def stop(self):
        self._active = False
        self._running = False


    def activate(self):
        self._active = True


    def deactivate(self):
        self._active = False


    def setactive(self, active):
        self._active = active