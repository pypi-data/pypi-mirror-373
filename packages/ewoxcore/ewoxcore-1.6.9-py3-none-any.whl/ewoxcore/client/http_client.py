from typing import Any, List, Dict, Text, Mapping, Iterable, IO, Optional, Tuple, Union, Awaitable
from datetime import date, datetime, timedelta
import requests
from requests.sessions import Session
from requests_toolbelt.utils import dump
from urllib3.util.retry import Retry
from ewoxcore.client.timeout_adapter import TimeoutAdapter


class HTTPClient():
    def __init__(self, total:int=3, backoff_factor:float=0.5, 
                status_forcelist:List[int]=[429, 500, 502, 503, 504], 
                method_whitelist:Optional[List[str]]=None, add_logging:bool=False, 
                proxies:Dict[str,str]=None) -> None:
        self._add_logging:bool = add_logging
        self._retry:Retry = None
        self._proxies:Dict[str,str] = proxies
        if (method_whitelist is not None):
            self._retry = Retry(
                    total=total,
                    backoff_factor=backoff_factor,
                    status_forcelist=status_forcelist,
                    method_whitelist=method_whitelist
            )
        else:
            self._retry = Retry(
                    total=total,
                    backoff_factor=backoff_factor,
                    status_forcelist=status_forcelist,
            )


    def session(self, timeout:float=15) -> Session:
        """ Create a new HTTP session with the specified timeout and retry settings. """
#        adapter = HTTPAdapter(max_retries=self._retry)
        adapter = TimeoutAdapter(max_retries=self._retry, timeout=timeout)
        session = requests.Session()
        if (self._proxies):
                session.proxies.update(self._proxies)

        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if (self._add_logging):
                session.hooks["response"] = [self._logging_hook]
        
        return session


    def _logging_hook(self, response, *args, **kwargs) -> None:
        data = dump.dump_all(response)
        print(data.decode('utf-8'))


#    def post(self, url:str, data:_Data, headers:Optional[Any]=None, timeout_seconds:float=15) -> Response:
#        pass



if __name__ == "__main__":
    client = HTTPClient(add_logging=True)
    session = client.session()
    print(session)
    response = session.get("https://api.openaq.org/v1/cities", params={"country": "BA"})
    print(response)

    