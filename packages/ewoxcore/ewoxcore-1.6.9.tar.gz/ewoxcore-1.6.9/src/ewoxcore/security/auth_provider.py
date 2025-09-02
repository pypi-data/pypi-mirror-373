from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, time, datetime, timedelta, timezone
from dateutil import parser
from ewoxcore.security.models.token import Token
from ewoxcore.utils.json_util import JsonUtil
from ewoxcore.utils.dictionary_util import DictionaryUtil

T = TypeVar("T")
Y = TypeVar("Y")


class AuthProvider():
    def __init__(self, ttl_seconds:int):
        self._ttl:int = ttl_seconds


    def get_token(self, user_id:str, data:T, encrypt:Callable[[str], str]) -> str:
        now_utc:datetime = datetime.now(tz=timezone.utc)
        data_enc:str = JsonUtil.serializeJson64(data)
        token = Token(user_id, now_utc, data_enc)
        json_enc:str = JsonUtil.serialize(token)
        token_enc:str = encrypt(json_enc)

        return token_enc


    def validate(self, class_type:Y, user_id:str, token:str, decrypt:Callable[[str], str]) -> Y:
        """ Returns none if token is not valid, otherwise a model based on class type."""
        now_utc:datetime = datetime.now(tz=timezone.utc)
        json_dec:str = decrypt(token)
        token_dec:Token = JsonUtil.deserialize_gen_object(Token, json_dec)
        token_exp:datetime = parser.parse(token_dec.expireAt)
        if ((now_utc < token_exp) | 
            (user_id != token_dec.userId)):
            return None

        model:Y = JsonUtil.deserialize_json64(class_type, token_dec.data)
        return model

    """
    def convert_dict_to_string(dict_data):
        return json.dumps(dict_data)


    def convert_string_to_dict(string_data):
        return json.loads(string_data)
    
    def _add_expiry_time(self, data):
        datetime.now(tz=timezone.utc)
        data_dict = {"data": data, "expiry": str(datetime.datetime.now())}
        string_data_dict = convert_dict_to_string(data_dict)
        return string_data_dict

    def get_token(self, data:Optional[Any]=None):
        expiry_added_data = self._add_expiry_time(data)
        encrypted_data = self.fernet.encrypt(expiry_added_data)
        return encrypted_data

    def _is_token_valid(self, data_dict):
        # check if data dicts contains valid keys
        data = data_dict.get("data", None)
        expiry = data_dict.get("expiry", None)
        is_token_valid = data != None or expiry != None

        # Check if token is expired
        time_difference = get_datetime_difference(
            parser.parse(expiry), datetime.datetime.now()
        )

        is_not_expired = time_difference < float(self.ttl_in_second)

        if is_token_valid and is_not_expired:
            return True
        return False

    def get_data(self, cipher_text):
        decrypted_token = self.fernet.decrypt(cipher_text)

        if not decrypted_token:
            return "Invalid token"

        data_dict = convert_string_to_dict(decrypted_token)

        if self._is_token_valid(data_dict):
            return data_dict.get("data")
        else:
            return "Invalid token"
    """

"""
# Initialize JWT with time to live in second.
jwt = JWT(ttl_in_second=2)

data = "my awesome data"
token = jwt.get_token(data)
print(token)

print("\n")
text = jwt.get_data(token)
print(text)
"""


"""
from jose import jwt
token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJ2YWx1ZSJ9.FG-8UppwHaFp1LgRYQQeS6EDQF7_6-bMFegNucHjmWg'

jwt.decode(token, 'secret', algorithms=['HS256'])
{u'key': u'value'}
"""


"""
class TestModel():
    def __init__(self):
        self.name:str = "Dude"


if __name__ == "__main__":
    from ewoxcore.security.fernet_provider import FernetProvider
    key:str = FernetProvider.generate_key()
    enc_prov = FernetProvider(key)

    user_id:str = "111"
    model = TestModel()
    prov = AuthProvider(1)
    token_data:str = prov.get_token(user_id, model, enc_prov.encrypt)
    model_dec:TestModel = prov.validate(TestModel, user_id, token_data, enc_prov.decrypt)
    print("")
"""