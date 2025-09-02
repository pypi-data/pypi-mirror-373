from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from lagom import Container, Singleton, ExplicitContainer
from lagom.exceptions import InvalidDependencyDefinition, DependencyNotDefined
from ewoxcore.service.interfaces.iservice_collection import IServiceCollection
from ewoxcore.service.interfaces.iservice_provider import IServiceProvider
from ewoxcore.service.service_provider import ServiceProvider

T = TypeVar('T')
C = TypeVar('C')


class ServiceCollection(IServiceCollection):
    """ Dependency Injection Container 
    https://lagom-di.readthedocs.io/en/latest/ 
    """
    def __init__(self) -> None:
        self._container =  ExplicitContainer()
        self.add_singleton(ServiceProvider, ServiceProvider())


    def add_setting(self, type:T, impl:C) -> None:
        self.add_singleton(type, impl)


    def add_singleton(self, type:T, impl:C) -> None:
        self._container[type] = Singleton(impl)


    def add_transient(self, type:T, impl:C) -> None:
        self._container[type] = impl


    def _get_service(self, type:T) -> T:
        try:
            return self._container[type]
        except Exception as error:
            print(error)
            return None


    def build_service(self) -> IServiceProvider:
        prov:ServiceProvider = self._get_service(ServiceProvider)
        prov.add_service(self._get_service)

        return prov
