from typing import Any, Optional, Dict, Tuple, Text, List
import validators
import re


class StringUtil:

    @staticmethod
    def get_safe_name(name:str) -> str:
        safe_name:str = re.sub("[^A-Za-z0-9--_]", '', name)
        return safe_name


    @staticmethod
    def strip_html(text:str) -> str:
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        no_tags = tag_re.sub('', text)
        return no_tags


    @staticmethod
    def is_email(input:str) -> bool:
        try:
            res:bool = validators.email(input)
            return True if (res) else False
        except:
            return False


    @staticmethod
    def extract_tags(text:str, begin:str="<%", end:str="%>") -> List[Tuple[str, str, str]]:
        return re.findall('('+begin+')(.+?)('+end+')', text, re.DOTALL)


    @staticmethod
    def extract_tag_keys(text:str, begin:str="<%", end:str="%>") -> List[str]:
        tups:List[Tuple[str, str, str]] = StringUtil.extract_tags(text, begin, end)
        keys:List[str] = []
        for tb, key, te in tups:
            if (key not in keys):
                keys.append(key)
        return keys


    @staticmethod
    def title_capitalized(text:str) -> str:
        """ Returns only the first letter in upper case. """
        if (text == ""):
            return ""
        return text[0].upper() + text[1:]


    @staticmethod
    def get_safe_string(val:str) -> str:
        if (val is None):
            return ""
        return str(val)


    @staticmethod
    def strip_end(val:str, ch:str) -> str:
        res:List[str] = val.split(ch)
        return res[0]


    @staticmethod
    def capitalize_camelcase_words(val:str) -> str:
        def camel_case_segment(segment):
            parts = re.split(r'[_\-]', segment)
            if not parts:
                return ''
            # Join camel case inside the segment but keep casing (just capitalize first char of each part except first)
            camel_cased = parts[0] + ''.join(p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in parts[1:])
            return camel_cased

        def process_word(word):
            camel_word = camel_case_segment(word)
            # Capitalize first letter of the whole word
            return camel_word[0].upper() + camel_word[1:] if camel_word else ''

        # Split by spaces but keep spaces
        tokens = re.split(r'(\s+)', val)
        result = [process_word(token) if token.strip() else token for token in tokens]
        return ''.join(result)
