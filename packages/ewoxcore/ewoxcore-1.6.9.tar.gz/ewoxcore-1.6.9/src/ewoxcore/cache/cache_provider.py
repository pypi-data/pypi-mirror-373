from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
from ewoxcore.cache.cache import Cache
from ewoxcore.cache.icache_provider import ICacheProvider
from ewoxcore.utils.json_util import JsonUtil

T = TypeVar("T")


class CacheProvider(ICacheProvider):
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if CacheProvider.__instance == None:
            CacheProvider()
        return CacheProvider.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if CacheProvider.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CacheProvider.__instance = self
            self.cache = Cache()


    def activate_expiration(self, timer_interval:int) -> None:
        self.cache.activate_expiration(timer_interval)


    def change_use_local(self, use_local:bool) -> None:
        """ Supported only by distributed cache provider. """
        pass


    def set_cache_size(self, size:int) -> None:
        self.cache.set_cache_size(size)


    async def get(self, cacheKey:str) -> Any:
        return self.cache.get(cacheKey)


    async def insert(self, cacheKey:str, cacheValue:Any) -> None:
        self.cache.insert(cacheKey, cacheValue)


    async def remove(self, cacheKey:str) -> None:
        self.cache.remove(cacheKey)


    async def get_all_values(self) -> List[Any]:
        return self.cache.get_all_values()


    async def add(self, key:str, value:str, absolute_expiration:timedelta) -> None:
        self.cache.add(key, value, absolute_expiration=absolute_expiration)


    async def add_expire_at(self, key:str, value:str, expire_at:datetime) -> None:
        self.cache.add_expire_at(key, value, expire_at=expire_at)


    async def clear(self) -> None:
        self.cache.clear()


    async def add_ext(self, key:str, value:T, absolute_expiration:timedelta) -> None:
        value_internal:str = JsonUtil.serializeJson64(value)
        self.add(key, value_internal, absolute_expiration)


    async def add_expire_at_ext(self, key:str, value:T, expire_at:datetime) -> None:
        value_internal:str = JsonUtil.serializeJson64(value)
        self.add_expire_at(key, value_internal, expire_at)


    async def insert_ext(self, key:str, value:T) -> None:
        value_internal:str = JsonUtil.serializeJson64(value)
        self.insert(key, value_internal)


    async def get_ext(self, class_type:T, key:str) -> T:
        value_enc:str = await self.get(key)
        return JsonUtil.deserialize_json64(class_type, value_enc)
