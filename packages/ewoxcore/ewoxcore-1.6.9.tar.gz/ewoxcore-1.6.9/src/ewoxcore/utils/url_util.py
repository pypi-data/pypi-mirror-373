from typing import Any, Optional, Dict, Tuple, Text, List
import re
import urllib
import hashlib
import shortuuid
import validators


class UrlUtil:
    def __init__(self):
        pass
    

    @staticmethod
    def get_safe_url(name:str, with_short_id:bool = True) -> str:
        name = name.replace(" ","-").replace("~","-").lower()
        name = re.sub('[^A-Za-z0-9\\-]+', '', name)
#        url:str = urllib.parse.quote(name).replace("~","-")
        url:str = urllib.parse.quote(name)
        if (with_short_id):
            short_id:str = shortuuid.uuid()
            url += "-" + short_id
        return url


    @staticmethod
    def get_hash_code(url:str) -> str:
        return hashlib.md5(url.encode('utf-8')).hexdigest()


    @staticmethod
    def safe_trailing_slash(url:str) -> str:
        url_last_ch:str = url[len(url)-1:]
        if (url_last_ch != "/"):
            url += "/"
        return url


    @staticmethod
    def get_query_params(url:str) -> Dict:
        if ("?" in url):
            url = url.split("?")[1]
        params = urllib.parse.parse_qsl(url)

        params_dict:Dict = dict(params)       
        return params_dict


    @staticmethod
    def is_url(url:str) -> bool:
        try:
            res:bool = validators.url(url)
            return True if (res) else False
        except:
            return False


if __name__ == "__main__":
    url:str = "userId=234&EI=1&transport=websocket"
    params = UrlUtil.get_query_params(url)
    print(params)
    
    url:str = "http://test.com?userId=234&EI=1&transport=websocket"
    params = UrlUtil.get_query_params(url)
    print(params)
