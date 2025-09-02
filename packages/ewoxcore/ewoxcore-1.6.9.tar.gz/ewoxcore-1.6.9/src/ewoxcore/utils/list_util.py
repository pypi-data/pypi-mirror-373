from typing import Any, Optional, Dict, Tuple, Text, List


class ListUtil:
    def __init__(self):
        pass
    

    @staticmethod
    def split(str_list:List[str], separator:str) -> List[List[str]]:
        splitted:List[List[str]] = []
        tmp_list:List[str] = []
        for i, s in enumerate(str_list):
            if (s != separator):
                tmp_list.append(s)
            else:
                splitted.append(tmp_list)
                tmp_list = []

        if (len(tmp_list) > 0):
            splitted.append(tmp_list)

        return splitted


    @staticmethod
    def to_string(str_list:List[str], separator:str = ",") -> str:
        s:str = separator.join(str_list)
        return s
