from typing import Any, Optional, Dict, Tuple, Text, List


class BooleanUtil:
    @staticmethod
    def is_bool(val:str) -> bool:
        try:
            if ((val.lower() == "true") | (val.lower() == "false")):
                return True
        except:
            return False


    @staticmethod
    def get_safe_bool(val:str) -> bool:
        if (val is None):
            return False
        return True if (str(val).lower() == "true") else False
