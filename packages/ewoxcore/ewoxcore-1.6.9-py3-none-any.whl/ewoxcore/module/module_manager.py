import os
import sys
import logging
import importlib
from typing import Any, List, Dict, Text, Optional, Tuple, Union
import ewoxcore.utils.file_util as file_utils


class ModuleManager:
    def __init__(self) -> None:
        self.classes = dict()


    def load_module_test(self, moduleName:str, className:str) -> Any:
        module_dir, module_file = os.path.split("modules/coachbot/actions/action_article.py")
        module_name, module_ext = os.path.splitext(module_file)
        spec = importlib.util.spec_from_file_location(module_name,"modules/coachbot/actions/action_article.py")
        module = spec.loader.load_module()
        class_ = getattr(module, className)


    def load_module(self, moduleName:str, className:str) -> Any:
        try:
            module = importlib.import_module(moduleName)          
            class_ = getattr(module, className)
            self.classes[className] = class_
        except (ImportError, NameError, SyntaxError) as err:
            logging.error("Error loading module", exc_info=True)

        return class_


    def get_class(self, className:str) -> Any:
        return self.classes[className]


    def get_class_instance(self, className:str) -> Any:
        class_ = self.classes[className]
        return class_()
