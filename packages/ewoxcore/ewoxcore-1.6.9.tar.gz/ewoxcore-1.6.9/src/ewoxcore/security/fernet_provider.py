from typing import Any, Optional, Dict, Tuple, Text, List
from cryptography.fernet import Fernet, InvalidToken


class FernetProvider():
    def __init__(self, key:str):
        self._fernet = Fernet(key=key.encode("utf-8"))


    @staticmethod
    def generate_key() -> str:
        key:bytes = Fernet.generate_key()
        return key.decode("utf-8")


    def encrypt(self, value:str) -> str:
        enc:bytes = self._fernet.encrypt(value.encode("utf-8"))
        return enc.decode("utf-8")


    def decrypt(self, value:str) -> Optional[str]:
        dec:bytes = None
        
        try:
            dec = self._fernet.decrypt(value.encode("utf-8"))
        except InvalidToken:
            return None

        return dec.decode("utf-8")


if __name__ == "__main__":
    key:str = FernetProvider.generate_key()
    prov = FernetProvider(key)
    enc:str = prov.encrypt("Dude has a car")
    dec:str = prov.decrypt(enc)
    print(dec)

