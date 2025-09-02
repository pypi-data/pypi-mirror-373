import logging
from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, overload
from datetime import date, datetime, timedelta
import random
import time
import threading
from sortedcontainers import SortedDict
from ewoxcore.cache.timer_ext import TimerExt


class Cache():
    def __init__(self, size:int = 10, use_expired_queue:bool=False, timer_interval:int=60):
        self._cache:dict = {}
        self._requested_at:dict = {}
        self._expirations:SortedDict = SortedDict()
        self._cache_size:int = size
        self._lock = threading.Lock()
        self._timer:TimerExt = None
        if (use_expired_queue):
            self._expiration_start(timer_interval)

    
    def activate_expiration(self, timer_interval:int) -> None:
        """ timer interval in seconds. """
        self._expiration_start(timer_interval)


    def _expiration_start(self, timer_interval:int) -> None:
        if (self._timer is not None):
            self._timer.stop()
            self._timer = None

        self._timer = TimerExt(self._remove_expired, timer_interval, True)
        self._timer.start()


    def set_cache_size(self, size:int) -> None:
        with self._lock:
            self._cache_size = size


    def contains(self, key:str) -> bool:
        with self._lock:
            if (key in self._cache):
                return True
            return False


    def get_allocated_size(self) -> int:
        length:int = 0
        with self._lock:
            length = len(self._cache)
        return length


    def get(self, key:str) -> Any:
        """
        Retrieve an object from our cache, keeping note of the time we last 
        retrieved it. 
        """
        with self._lock:
            if key in self._cache:
                self._requested_at[key] = time.time()
                return self._cache[key]
            else:
#                raise KeyError("Not found!")
                return None


    def insert(self, key:str, value:Any) -> None:
        """
        Insert a new object into our cache. If inserting would exceed our cache size,
        then we shall make room for it by removing the least recently used. 
        """
        with self._lock:
            if len(self._cache) == self._cache_size:
                self._remove_least_recently_used()

        self._cache[key] = value
        self._requested_at[key] = time.time()


    def _remove_least_recently_used(self):
        if self._requested_at:
            # find key with the lowest timestamp.
            leastRecentlyUsedKey = min(self._requested_at, key=lambda cacheKey: self._requested_at[cacheKey])

            self._cache.pop(leastRecentlyUsedKey, None)
            self._requested_at.pop(leastRecentlyUsedKey, None)
        else:
            # otherwise choose randomly.
            randomChoice = random.choice(self._cache.keys())
            self._cache.pop(randomChoice, None)


    def remove(self, key:str) -> None:
        with self._lock:
            self._cache.pop(key, None)


    def get_all_values(self) -> List[Any]:
        values:List[Any] = []
        with self._lock:
            for key, value in self._cache.items():
                values.append(value)

        return values


    def _remove_expired(self) -> None:
        try:
            now = datetime.now()
            now_num:int = int(now.strftime('%Y%m%d%H%M%S'))
            history:datetime = datetime.now() - timedelta(days=1)
            history_num:int = int(history.strftime('%Y%m%d%H%M%S'))
            keys_expired = self._expirations.irange(history_num, now_num)
            for key in keys_expired:
                with self._lock:
                    cache_key:str = self._expirations[key]
                    self._expirations.pop(key, None)
                self.remove(cache_key)
#            self._expiration_start()
        except Exception as error:
            logging.error(f"Cache remove expired. Error: {error}")


    def add(self, key:str, value:str, absolute_expiration:timedelta) -> None:
        now_time:datetime = datetime.now()
        now = now_time + absolute_expiration
        now_num:int = int(now.strftime('%Y%m%d%H%M%S'))
        self.insert(key, value)
        with self._lock:
            self._expirations[now_num] = key


    def add_expire_at(self, key:str, value:str, expire_at:datetime) -> None:
        at_num:int = int(expire_at.strftime('%Y%m%d%H%M%S'))
        self.insert(key, value)
        with self._lock:
            self._expirations[at_num] = key


    def clear(self) -> None:
        keys:List[str] = []
        for key in self._cache.keys():
            keys.append(key)

        for key in keys:
            self.remove(key)


if __name__ == "__main__":
    cache:Cache = Cache(use_expired_queue=True, timer_interval=2)
    
    cache.add("k1", "Dude", timedelta(seconds=1))
    while True:
        print("")
    cache._remove_expired()
    time.sleep(2)
    cache._remove_expired()