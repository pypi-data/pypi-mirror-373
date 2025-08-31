from functools import wraps
import re
from typing import Any, Callable, TypeVar

_C = TypeVar("_C", bound=Callable[..., Any])

class ExtController():

    @staticmethod
    def get_controller_name(inst_name:str)->str:
        if inst_name == 'Controller':
            return ''
        else:
            result = re.sub(r"(Controller)", '', inst_name, 0, re.MULTILINE)
            
        return result.lower()