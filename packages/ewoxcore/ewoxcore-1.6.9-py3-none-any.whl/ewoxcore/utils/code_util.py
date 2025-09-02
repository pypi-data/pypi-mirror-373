from typing import Any, Optional, Dict, Tuple, Text, List
from random import choice
from string import ascii_uppercase


class CodeUtil:
    @staticmethod
    def generate(len:int=6, to_lower:bool=True) -> str:
        val:str = ''.join(choice(ascii_uppercase) for i in range(len))
        return val.lower() if (to_lower) else val


if __name__ == "__main__":
    val:str = CodeUtil.generate()
    print(val)
