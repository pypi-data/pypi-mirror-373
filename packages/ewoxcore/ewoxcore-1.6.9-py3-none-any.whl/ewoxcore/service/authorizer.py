from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import datetime, timedelta, timezone
import os
import secrets
from jose import jwt, jwe, JWTError
from ewoxcore.service.interfaces.iauthorizer import IAuthorizer
from ewoxcore.utils.json_util import JsonUtil

T = TypeVar('T')


class Authorizer(IAuthorizer):
    def __init__(self, func = None):
        self._token_secret:str = os.getenv("JWT_SECRET")
        self._token_api_secret:str = os.getenv("JWT_API_SECRET")
        self._encryption_secret:bytes | None = None
        enc_key:str | None = os.getenv("JWT_ENCRYPTION_SECRET", None)
        if (enc_key):
            self._encryption_secret = bytes.fromhex(enc_key)
        self._algorithm:str = "HS256"
        self._issuer:str | None = os.getenv("JWT_ISSUER")
        self._token_timeout:int = 60 * 12  # Default timeout in minutes
        self._func_get_user = func


    def set_token_timeout(self, timeout: int) -> None:
        """ Set the token timeout in minutes. """
        self._token_timeout = timeout


    def create_token(self, model: T, expires_delta: timedelta=None):
        """ Create a JWT token with the given model and expiration delta. """
        payload:Dict[str, Any] = dict()
        if (self._issuer):
            payload.update({"iss": self._issuer})
        
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self._token_timeout))
        payload.update({"exp": expire})

        if (model):            
            json_enc = JsonUtil.serializeJson64(model)
            if (self._encryption_secret):
                json_enc = jwe.encrypt(json_enc, self._encryption_secret, algorithm='dir', encryption='A256GCM')
                json_enc = json_enc.decode('utf-8')

            payload.update({"data": json_enc})

        token:str = jwt.encode(payload, self._token_secret, algorithm=self._algorithm)

        return token


    def decode_token(self, token: str, class_type:T) -> Optional[T]:
        """ Decode the JWT token and return the model. """
        try:
            payload:Dict[str, Any] = []
            payload = jwt.decode(token, self._token_secret, algorithms=[self._algorithm], issuer=self._issuer)

            data:str = payload.get("data")
            if (self._encryption_secret):
                data_bytes:bytes = data.encode('utf-8')
                data = jwe.decrypt(data_bytes, self._encryption_secret)
    
            model:T = JsonUtil.deserialize_json64(class_type, data)

            return model
        except JWTError as e:
            print(f"JWT Error: {e}")
            return None
        

    def is_authorized(self, token:str, required_role:str = "") -> bool:
        """ Check if the token is authorized for the required role. Returns True if authorized, False if not authorized, and False if the token is invalid. """
        try:
            payload:Dict[str, Any] = []
            payload = jwt.decode(token, self._token_secret, algorithms=[self._algorithm], issuer=self._issuer)

            if (required_role != ""):
                roles:List[str] = payload["roles"]
                if (required_role in roles):
                    return True
                else:
                    return False
        except JWTError as e:
            print(f"JWT Error: {e}")
            return False

        return True

        

    def create_api_token(self, model: T, expires_delta: timedelta=None):
        """ Create an API JWT token with the given model and expiration delta. """
        payload:Dict[str, Any] = dict()
        if (self._issuer):
            payload.update({"iss": self._issuer})
        
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self._token_timeout))
        payload.update({"exp": expire})

        if (model):
            json_enc = JsonUtil.serializeJson64(model)
            payload.update({"data": json_enc})

        token:str = jwt.encode(payload, self._token_api_secret, algorithm=self._algorithm)
        
        return token


    def decode_api_token(self, token: str) -> Optional[T]:
        """ Decode the JWT token and return the model. """
        try:
            payload:Dict[str, Any] = []
            payload = jwt.decode(token, self._token_api_secret, algorithms=[self._algorithm], issuer=self._issuer)

            data:str = payload.get("data")
            model:T = JsonUtil.deserialize_json64(T, data)

            return model
        except JWTError:
            return None


    def generate_key_256(self) -> str:
        """ Generate a random 256-bit key for encryption. """
        return secrets.token_bytes(32).hex()
    

if __name__ == "__main__":
    from ewoxcore.security.models.token import Token
    
    auth = Authorizer()
    token_data = Token()
    token_data.data = "Test"

    token:str = auth.create_token(token_data)
    token_data_out:Token = auth.decode_token(token, Token)
    print(token_data_out.data)
