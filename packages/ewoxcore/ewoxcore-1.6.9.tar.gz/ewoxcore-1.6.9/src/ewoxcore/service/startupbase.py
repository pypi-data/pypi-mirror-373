from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
import os
from ewoxcore.constants.server_env import ServerEnv
from ewoxcore.localize.localize_provider import LocalizeProvider
from ewoxcore.monitoring.ilogger import ILogger
from ewoxcore.cache.icache_provider import ICacheProvider
from ewoxcore.cache.icache_local_provider import ICacheLocalProvider
from ewoxcore.cache.cache_provider import CacheProvider
from ewoxcore.monitoring.monitoring_event import MonitoringEvent
from ewoxcore.monitoring.monitoring_event_name import MonitoringEventName
from ewoxcore.localize.ilocalizer import ILocalizer
from ewoxcore.service.authorizer import Authorizer
from ewoxcore.service.interfaces.iauthorizer import IAuthorizer
from ewoxcore.service.interfaces.iservice_collection import IServiceCollection
from ewoxcore.configuration.configuration import Configuration
from ewoxcore.configuration.interfaces.iconfiguration_builder import IConfigurationBuilder
from ewoxcore.configuration.configuration_builder import ConfigurationBuilder
from ewoxcore.service.interfaces.istartup_internal import IStartupInternal
from ewoxcore.monitoring.simple_logger import SimpleLogger
from ewoxcore.monitoring.signal_handler import SignalHandler
from ewoxcore.service.service_identifier import ServiceIdentifier

T = TypeVar('T')


class StartupBase(IStartupInternal):
    def __init__(self) -> None:
        self._get_service:Callable[[Type[T]], T]=None
        self._configuration:Configuration = None


    def configure_services(self, service_name:str, service:IServiceCollection, get_service:Callable[[Type[T]], T]=None, use_unittest:bool=False) -> None:
        service.add_singleton(IConfigurationBuilder, lambda c: ConfigurationBuilder())
        service.add_singleton(ServiceIdentifier, lambda c: ServiceIdentifier(service_name))

        env:str = os.getenv(ServerEnv.ENVIRONMENT)
        builder:IConfigurationBuilder = get_service(IConfigurationBuilder)
        builder.add_json_file(f"data/settings/appbasesettings-{env}.json")


    def configure_defaults(self, service:IServiceCollection, get_service:Callable[[Type[T]], T]=None) -> None:
        self._get_service = get_service
        builder:IConfigurationBuilder = get_service(IConfigurationBuilder)
        self._configuration = builder.build()

        logger:ILogger = get_service(ILogger)
        if (logger is None):
            service.add_singleton(ILogger, lambda c: SimpleLogger())
            logger = get_service(ILogger)

        logger.setup()

        service.add_singleton(SignalHandler, lambda c: SignalHandler())

        cache_local:ICacheLocalProvider = get_service(ICacheLocalProvider)
        if (cache_local is None):
            service.add_singleton(ICacheLocalProvider, lambda c: CacheProvider())

        localizer:ILocalizer = get_service(ILocalizer)
        if (localizer is None):
            service.add_singleton(ILocalizer, lambda c: LocalizeProvider())

        authorizer:IAuthorizer = get_service(IAuthorizer)
        if (authorizer is None):
            service.add_singleton(IAuthorizer, lambda c: Authorizer())


    def setup(self, get_service:Callable[[Type[T]], T]=None) -> None:
        signal:SignalHandler = get_service(SignalHandler)
        signal.setup()

        cache_local:ICacheLocalProvider = get_service(ICacheLocalProvider)
        cache_local.activate_expiration(10)


    async def setup_async(self, get_service:Callable[[Type[T]], T]) -> None:
        self.setup(get_service)


    async def on_start(self) -> None:
        pass


    async def on_stop(self) -> None:
        pass


    async def dispose(self) -> None:
        pass