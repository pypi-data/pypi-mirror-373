from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod

T = TypeVar('T')


class IAuthorizer(ABC):
    @abstractmethod
    def set_token_timeout(self, timeout: int) -> None:
        """ Set the token timeout in minutes. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def create_token(self, model: T, expires_delta: timedelta=None):
        """ Create a JWT token with the given model and expiration delta. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def decode_token(self, token: str) -> Optional[T]:
        """ Decode the JWT token and return the model. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def is_authorized(self, token:str, required_role:str = "") -> bool:
        """ Check if the token is authorized for the required role. Returns True if authorized, False if not authorized, and False if the token is invalid. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def create_api_token(self, model: T, expires_delta: timedelta=None):
        """ Create an API JWT token with the given model and expiration delta. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def decode_api_token(self, token: str) -> Optional[T]:
        """ Decode the JWT token and return the model. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def generate_key_256(self) -> str:
        """ Generate a random 256-bit key for encryption. """
        raise NotImplementedError("Implement inhereted method")
