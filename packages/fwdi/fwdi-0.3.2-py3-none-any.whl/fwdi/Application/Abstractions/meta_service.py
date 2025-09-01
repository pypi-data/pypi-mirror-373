#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import inspect
from typing import Any, TypeVar

from ...Domain.Enums.type_methods import TypeMethod

from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Application.Logging.manager_logging import ManagerLogging

Self = TypeVar("Self")


class MetaServiceFWDI(type):
    def __init__(cls: type[Self], 
                 name:str, 
                 bases:tuple[type, ...], 
                 namespace:dict[str, Any],
                 /, **kwds: Any):
        
        from ...Utilites.ext_reflection import ExtReflection
        for attr, value in cls.__dict__.items():
            if callable(value):
                if attr == '__call__':
                    setattr(cls, attr, ExtReflection.init_inject(value))
                    
                if not attr.startswith('__') and not inspect.isabstract(cls):
                    method_signature = list(inspect.signature(value.__wrapped__ if hasattr(value, '__wrapped__') else value).parameters.values())
                    signature_has_self = True if len([item for item in method_signature if item.name == 'self']) > 0 else False
                    type_call = ExtReflection.get_type_method(value, signature_has_self)

                    match type_call:
                        case TypeMethod.Instance:
                            if inspect.iscoroutinefunction(value):
                                setattr(cls, attr, ExtReflection._inject_inst_async(value))
                            else:
                                setattr(cls, attr, ExtReflection._inject_inst_sync(value))
                        case TypeMethod.Static:
                            if inspect.iscoroutinefunction(value):
                                setattr(cls, attr, ExtReflection._inject_static_async(value))
                            else:
                                setattr(cls, attr, ExtReflection._inject_static_sync(value))
        
        if not inspect.isabstract(cls):
            if hasattr(cls, '__name__'):
                cls.__log__:BaseSysLogging = ManagerLogging.get_logging(cls.__name__)
        
        super().__init__(name, bases, namespace)