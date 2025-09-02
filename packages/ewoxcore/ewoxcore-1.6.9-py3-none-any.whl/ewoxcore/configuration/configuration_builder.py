from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
import json
from ewoxcore.configuration.configuration import Configuration
from ewoxcore.configuration.interfaces.iconfiguration_builder import IConfigurationBuilder


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self) -> None:
        self._configuration:Configuration = Configuration()


    def build(self) -> Configuration:
        return self._configuration


    def add_json_file(self, path:str) -> IConfigurationBuilder:
        try:
            with open(path) as f:
                data:Dict = json.load(f)
                self._configuration.add(data)
        except (Exception) as error:
            pass

        return self
