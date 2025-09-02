import json
from datetime import date, datetime, timedelta
from decimal import *
from enum import *

class DateTimeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object,
                            *args, **kargs)


    def dict_to_object(self, d):
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        try:
            dateobj = datetime(**d)
            return dateobj
        except:
            d['__type__'] = type
            return d


    def json_default_format(value):
        try:
            if isinstance(value, datetime):
                return {
                    '__type__': 'datetime',
                    'year': value.year,
                    'month': value.month,
                    'day': value.day,
                    'hour': value.hour,
                    'minute': value.minute,
                    'second': value.second,
                    'microsecond': value.microsecond,
                }
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, Enum):
                return value.name
            else:
                return vars(value)
        except Exception as e:
            raise ValueError
