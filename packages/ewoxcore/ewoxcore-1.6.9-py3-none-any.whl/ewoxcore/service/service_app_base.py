from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import os
import uuid
import asyncio
from ewoxcore.monitoring.ilogger import ILogger
from ewoxcore.constants.server_env import ServerEnv
from ewoxcore.service.interfaces.iservice import IService
from ewoxcore.service.interfaces.iservice_collection import IServiceCollection
from ewoxcore.service.interfaces.iservice_provider import IServiceProvider
from ewoxcore.service.interfaces.istartup_internal import IStartupInternal
from ewoxcore.monitoring.simple_logger import SimpleLogger
from ewoxcore.monitoring.signal_handler import SignalHandler
from ewoxcore.service.interfaces.istartup import IStartup
from ewoxcore.service.service_collection import ServiceCollection
from ewoxcore.service.startupbase import StartupBase
from ewoxcore.service.service import add_service

T = TypeVar('T')


class ServiceAppBase():
    def __init__(self, service_name:str="", startup:IStartup=None, service:IService=None) -> None:
        self._startup:IStartup = startup
#        self._service:IService = service if (service) else ServiceBase()
        # self._service_id:str = str(uuid.uuid4())
        self._service_name:str = service_name
        self._startup_internal:IStartupInternal = StartupBase()
        self._service_collection:IServiceCollection = ServiceCollection()
        self.get_service:Callable[[Type[T]], T] = None

#        is_debug:bool = False if (os.getenv(ServerEnv.ENVIRONMENT) == ServerEnv.PRODUCTION) else True


    async def on_start(self) -> None:
        """ Called on start up. Inheret this method. """
        pass


    async def on_stop(self) -> None:
        """ Called on stop. Inheret this method. """
        pass


    async def _on_stop(self) -> None:
        await self._startup_internal.on_stop()
        await self.on_stop()
        await self._startup_internal.dispose()


    async def _start_async(self) -> None:
        service_provider:IServiceProvider = self._service_collection.build_service()
        self.get_service = service_provider.get_service
        add_service(self.get_service)


        self._startup_internal.configure_services(self._service_name, self._service_collection, self.get_service)

        if (self._startup):
            self._startup.configure_services(self._service_collection, self.get_service)

        self._startup_internal.configure_defaults(self._service_collection, self.get_service)
        await self._startup_internal.setup_async(self.get_service)
        if (self._startup):
#            self._startup.setup(self.get_service)
            await self._startup.setup_async(self.get_service)

        signal:SignalHandler = self.get_service(SignalHandler)
        signal.set_callback(self._on_stop)

#        logger:ILogger = self.get_service(ILogger)
 #       if (self._service):
 #           await self._service.setup(self.get_service)

        await self._startup_internal.on_start()
        await self.on_start()

#        logger.info(f"Environment: {server_env}, Port: {server_port} ")
#        await asyncio.Future()

"""
    def start(self, server_port:int = 80, debug_server_port:int=0) -> None:
        uvloop.install()
        server_env:str = os.getenv(ServerEnv.ENVIRONMENT)
        if ((server_env == ServerEnv.DEVELOPMENT) & (debug_server_port != 0)):
            server_port = debug_server_port

        asyncio.run(self._start_async(server_port))
"""
