from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
import logging
import os
from ewoxcore.constants.server_env import ServerEnv
from ewoxcore.monitoring.ilogger import ILogger
from ewoxcore.monitoring.models.log_event import LogEvent

T = TypeVar('T')


class SimpleLogger(ILogger):
    def __init__(self) -> None:
        pass


    def setup(self) -> None:
        server_env:str = os.getenv(ServerEnv.ENVIRONMENT)
        if (server_env == ServerEnv.PRODUCTION):
            logging.basicConfig(format='%(levelname)s:%(message)s')
        else:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
            logging.debug("Start logging at debug level.")


    def info(self, message:str, *args, **kwargs) -> None:
        logging.info(message, *args, **kwargs)


    def warning(self, message:str, *args) -> None:
        logging.warning(message, *args)


    def error(self, message:str, *args) -> None:
        if (args):
            logging.error(message, *args, exc_info=True)
        else:
            logging.error(message, *args, exc_info=False)


    def debug(self, message:str, *args) -> None:
        logging.debug(message, *args)


    def info_ext(self, event:LogEvent) -> None:
        logging.info(event.message)


    def warning_ext(self, event:LogEvent) -> None:
        logging.warning(event.message)


    def error_ext(self, event:LogEvent) -> None:
        logging.error(event.message, exc_info=False)


    def debug_ext(self, event:LogEvent) -> None:
        logging.debug(event.message)


    def log_scoped(self, level: str, message: str, args: Optional[T] = None) -> None:
        pass
