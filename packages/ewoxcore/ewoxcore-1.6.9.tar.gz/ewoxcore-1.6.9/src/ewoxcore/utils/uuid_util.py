from typing import Any, Optional, Dict, Tuple, Text, List
import uuid


class UUIDUtil:
    @staticmethod
    def is_valid(id:str) -> bool:
        try:
            uuid.UUID(id)
            return True
        except ValueError:
            return False
        except:
            return False
