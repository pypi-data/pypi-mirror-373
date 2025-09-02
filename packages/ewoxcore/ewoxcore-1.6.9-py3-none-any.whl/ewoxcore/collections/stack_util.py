from typing import Any, Optional, Dict, Tuple, Text, List
from ewoxcore.collections.stack import Stack


class StackUtil:
    @staticmethod
    def push_range_preserve_order(source:Stack, collection:List[Any]) -> None:
        """ Push list of T onto the stack and preserver the order of the list (first one in the list is last in the stack). """
        for i in reversed(range(len(collection),-1,-1)):
            if (i < len(collection)):
                source.push(collection[i])
