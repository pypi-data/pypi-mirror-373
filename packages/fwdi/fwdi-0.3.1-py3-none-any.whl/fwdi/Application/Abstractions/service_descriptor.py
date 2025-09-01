#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import abc
import inspect
import logging
from typing import TypeVar

from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Application.Logging.manager_logging import ManagerLogging
from ...Domain.Enums.type_methods import TypeMethod
from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Domain.Enums.service_life import ServiceLifetime

_CLS_ = TypeVar('T', bound='ServiceDescriptorFWDI')
T = TypeVar('_CLS')

class ServiceDescriptorFWDI():
    def __init__(self) -> None:
        self.ServiceType: type[T] = None
        self.ImplementationType: type[T] = None
        self.Implementation:T = None
        self.Lifetime:ServiceLifetime = None
	
    @classmethod
    def create_from_instance(cls: type[_CLS_], inst:T, lifetime:ServiceLifetime)-> _CLS_:
        new_instance = cls()
        new_instance.ServiceType = type(inst)
        new_instance.ImplementationType = new_instance.ServiceType
        new_instance.Implementation = ServiceDescriptorFWDI.__set_inject_v2(inst)
        new_instance.Lifetime = lifetime

        return new_instance

    @classmethod
    def create_from_type(cls: type[_CLS_], inst_type:type[T] , lifetime:ServiceLifetime)-> _CLS_:
         new_instance = cls()
         new_instance.ServiceType = inst_type
         new_instance.ImplementationType = ServiceDescriptorFWDI.__set_inject_v2(inst_type)
         new_instance.Lifetime = lifetime

         return new_instance

    @classmethod
    def create(cls: type[_CLS_], base_type:type[T], inst_type:type[T], lifetime: ServiceLifetime)-> _CLS_:
        new_instance = cls()
        new_instance.ServiceType = base_type
        new_instance.ImplementationType = ServiceDescriptorFWDI.__set_inject_v2(inst_type)
        new_instance.Lifetime = lifetime

        return new_instance

    @classmethod
    def create_v2(cls: type[_CLS_], base_type:type[T], _instance:type[T], lifetime: ServiceLifetime)-> _CLS_:
        new_instance = cls()
        new_instance.ServiceType = base_type
        new_instance.ImplementationType = _instance
        new_instance.Implementation = ServiceDescriptorFWDI.__set_inject_v2(_instance)
        new_instance.Lifetime = lifetime

        return new_instance     
    
    @classmethod
    def create_log(cls: type[_CLS_], inst:T)-> _CLS_:
        new_instance = cls()
        new_instance.ServiceType = inst
        new_instance.ImplementationType = inst
        new_instance.Implementation = ServiceDescriptorFWDI.__set_inject_log_v1(inst)

        return new_instance

    def __set_inject_v2(cls):
        from ...Utilites.ext_reflection import ExtReflection

        for attr, value in cls.__dict__.items():
            if callable(value):
                if attr == '__init__' or attr == '__call__':
                    setattr(cls, attr, ExtReflection._inject_inst_sync(value))
                
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
                if GlobalSettingService.log_lvl == logging.DEBUG:
                    print(f"Set attribute __log__ to :{cls}")

                cls.__log__:BaseSysLogging = ManagerLogging.get_logging(cls.__name__, GlobalSettingService)
        
        return cls

    def __set_inject_log_v1(cls:type[any]):

        if not inspect.isabstract(cls):
            if hasattr(cls, '__name__'):
                if GlobalSettingService.log_lvl == logging.DEBUG:
                    print(f"Set attribute __log__ to :{cls}")

                cls.__log__:BaseSysLogging = ManagerLogging.get_logging(cls.__name__, GlobalSettingService)
        
        return cls