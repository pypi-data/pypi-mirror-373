from typing import Any, Optional, Dict, Tuple, Text, List
import re


class LanguageUtil:
    @staticmethod
    def is_valid(language_code:str, fast_check:bool=False) -> bool:
        try:
            if (fast_check):
                if (len(language_code) != 5):
                    return False
                return True
            else:
                pattern:str = "^[a-z]{2}-[A-Z]{2}$"
                res:re.Match = re.match(pattern, language_code)
                return True if (res) else False
        except ValueError:
            return False
        except:
            return False


if __name__ == "__main__":
    res:bool = LanguageUtil.is_valid("en-GB")
    print(res)
    res:bool = LanguageUtil.is_valid("e1-GB")
    print(res)
    res:bool = LanguageUtil.is_valid("en-gb")
    print(res)
