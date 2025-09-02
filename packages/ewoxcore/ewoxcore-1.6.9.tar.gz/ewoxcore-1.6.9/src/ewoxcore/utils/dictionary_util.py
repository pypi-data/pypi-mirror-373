from typing import Any, Optional, Dict, Tuple, Text
import inspect


class DictionaryUtil:
    def __init__(self):
        pass
    

    @staticmethod
    def get(dict:Dict, name:str, default:Any) -> Any:
        return dict[name] if (name in dict) else default


    @staticmethod
    def to_dict(obj) -> Dict[str, Any]:
        d = {}
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith('__') and not inspect.ismethod(value):
                d[name] = value
        return d
    
    
    @staticmethod
    def convert(model:Any) -> Dict:
        d = dict((name, getattr(model, name)) for name in dir(model) if not name.startswith('__') and not inspect.ismethod(name))

        return d


    """ NOT WORKING
    # Support recursive class structure as well as datetime
    @staticmethod
    def convert(model:Any) -> Dict:
        return json.loads(
            json.dumps(model, indent=4, separators=(',', ': ')), cls=DateTimeDecoder)
    """