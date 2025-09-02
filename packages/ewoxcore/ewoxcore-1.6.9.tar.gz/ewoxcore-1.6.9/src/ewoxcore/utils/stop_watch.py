from typing import Any, List, Optional, Dict, Tuple, Text
from datetime import date, time, datetime, timedelta, timezone


class StopWatch():
    def __init__(self) -> None:
        self._is_running:bool = False
        self._start_at:time = None
        self._stop_at:time = None


    def start(self) -> datetime:
        self._start_at = datetime.now()
        return self._start_at


    def stop(self) -> datetime:
        self._stop_at = datetime.now()
        return self._stop_at


    def elapsed(self) -> timedelta:
        delta:timedelta = self._stop_at - self._start_at
        return delta


if __name__ == "__main__":
    sw = StopWatch()
    sw.start()
    sw.stop()
    sw.elapsed()
