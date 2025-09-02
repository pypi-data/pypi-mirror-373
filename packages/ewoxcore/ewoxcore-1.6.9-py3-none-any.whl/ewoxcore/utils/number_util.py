from typing import Any, Optional, Dict, Tuple, Text, List
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR
import numpy as np


class NumberUtil:
    @staticmethod
    def is_float(val:str) -> bool:
        try:
            num:float = float(val)
            return True
        except:
            return False


    @staticmethod
    def is_integer(val:str) -> bool:
        try:
            if (isinstance(val, int)):
                return True
            if (isinstance(val, float)):
                return False
            if (val is None):
                return False
            return val.isdigit()
        except:
            return False


    @staticmethod
    def get_safe_float(val:str, precision:Decimal=Decimal('.11111')) -> float:
        """ Get a safe float with a 5 digits rounding precision by default. """
        if ((val is None) | (val == "")):
            return 0
        dec = Decimal(str(val)).quantize(precision, rounding=ROUND_FLOOR)
        if (dec.is_nan()):
            return 0
        return float(dec)


    @staticmethod
    def get_safe_int(val:str, default_val:int=0) -> int:
        if (val is None):
            return default_val
        
        if (NumberUtil.is_integer(val) == False):
            return default_val

        val = int(val)
        if (np.isnan(val)):
            return default_val

        return int(val)
