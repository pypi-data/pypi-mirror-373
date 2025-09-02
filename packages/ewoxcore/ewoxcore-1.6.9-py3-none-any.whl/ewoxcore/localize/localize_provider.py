from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from i18n import config
from i18n import translations
from i18n import resource_loader
from i18n.translator import t
from ewoxcore.localize.ilocalizer import ILocalizer


class LocalizeProvider(ILocalizer):
    def __init__(self) -> None:
        self._languages:dict = {}
        self._languages["en-GB"] = "en"
        self._path:str = "./data/translations"


    def register(self, language_code:str, language_two_letter:str) -> None:
        self._languages[language_code] = language_two_letter


    def _get_language(self, language_code:str) -> str:
        if language_code in self._languages:
            return self._languages[language_code]
        return "en"

    
    def setup(self, path:str="", default_language:str="en-GB") -> None:
        load_path:str = path if (path != "") else self._path
        config.set("file_format", "json")
        config.set("load_path", [load_path])
        config.set("filename_format", "{locale}.{format}")
        config.set('skip_locale_root_data', True)
        config.set("locale", self._get_language(default_language))
        resource_loader.init_json_loader()
        translations.has("foo") # to start loading files to memory.


    def get(self, key:str, language_code:str="en-GB") -> str:
        text:str = t(key, locale=self._get_language(language_code))
        return text
