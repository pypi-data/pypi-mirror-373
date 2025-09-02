from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
from requests.models import Response
from requests.sessions import Session
from ewoxcore.client.http_client import HTTPClient
from ewoxcore.client.status_code import StatusCode
from ewoxcore.utils.json_util import JsonUtil

T = TypeVar("T")


class GraphQLClient():
    def __init__(self, url:str, token:str, request_timeout:float = 90, auth_key:str="Authorization") -> None:
        self._url:str = url
        self._token:str = token
        self._request_timeout:float = request_timeout
        self._headers:Dict[str, str] = {auth_key : self._token}


    def post(self, class_type:T, query:str, variables:str="") -> Optional[T]:
        if (not query):
            return None

        client = HTTPClient()
        session:Session = client.session(timeout=self._request_timeout)
        response:Response = None
        if (variables):
            response = session.post(url=self._url, json={"query": query, "variables": variables}, headers=self._headers)
        else:
            response = session.post(url=self._url, json={"query": query}, headers=self._headers)
        if response.status_code != int(StatusCode.Ok):
            return None

        json_data:str = response.content.decode()
        json_obj:Dict = JsonUtil.deserialize(json_data)
        query_name:str = ""
        for key, value in json_obj["data"].items():
            query_name = key
            break

        data:str = json_obj["data"][query_name][0]["data"]
        model:T = JsonUtil.deserialize_json64(class_type, data)

        return model


if __name__ == "__main__":
    client = GraphQLClient("", "")
    client.post(Any, "dudd")
    print("")