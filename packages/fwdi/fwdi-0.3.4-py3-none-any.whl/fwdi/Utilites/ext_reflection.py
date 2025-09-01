#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import logging
import time
from functools import wraps
import inspect
import itertools
from types import FunctionType
from typing import Any, Awaitable, Coroutine, TypeVar, Callable, Union

from ..Utilites.utilities import Utilities

from ..Application.Abstractions.base_logging import BaseSysLogging

from ..Application.Logging.manager_logging import ManagerLogging
from ..Application.DependencyInjection.resolve_provider import *

from ..Domain.Configure.global_setting_service import GlobalSettingService
from ..Domain.Enums.type_methods import TypeMethod

T = TypeVar('T')
_C = TypeVar("_C", bound=Callable[..., Coroutine[None, None, T]])

class ExtReflection():
    count_inject_sync:int = 0
    count_inject_async:int = 0
    count_inject:int = 0
    __log__:BaseSysLogging = None

    @staticmethod
    def get_methods_class(cls):
        return set((x, y) for x, y in cls.__dict__.items()
                    if isinstance(y, (FunctionType, classmethod, staticmethod))
                    and not(x.startswith("__") and x.endswith("__")))

    @staticmethod
    def get_type_method(fn:_C, signature_has_self:bool)->TypeMethod:
        if not signature_has_self:
            return TypeMethod.Static
        else:
            if hasattr(fn, '__self__'):
                if inspect.isclass(fn.__self__):
                    return TypeMethod.Classmethod

        return TypeMethod.Instance
    
    @staticmethod
    def get_list_parent_methods(cls):
        return set(itertools.chain.from_iterable(
            ExtReflection.get_methods_class(c).union(ExtReflection.get_list_parent_methods(c)) for c in cls.__bases__))

    @staticmethod
    def list_class_methods(cls, is_narrow:bool):
        methods = ExtReflection.get_methods_class(cls)
        if is_narrow:
            parentMethods = ExtReflection.get_list_parent_methods(cls)
            return set(cls for cls in methods if not (cls in parentMethods))
        else:
            return methods
    
    @staticmethod
    def get_init_info_v1(fn:Callable[..., Any], *args, **kwargs)->dict:
            fn_datas:dict = {}
            fn_args:list[dict] = []

            fn_datas['args'] = args
            fn_datas['kwargs'] = kwargs
            fn_datas['class'] = inspect._findclass(fn)
            fn_datas['name'] = fn.__name__
            fn_datas['type'] = type(fn_datas['class'].__dict__[fn.__name__])
            fn_datas['type_method'] = ExtReflection.get_type_method(fn)
            fn_datas['return_type'] = fn.__annotations__['return'] if 'return' in fn.__annotations__ else None

            fn_params = inspect.signature(fn)
            for index, param_name in enumerate(fn_params.parameters):
                param_d = fn_params.parameters[param_name]
                type_param = param_d.annotation if not param_d.annotation is inspect._empty else inspect._empty
                fn_args.append({'arg_pos': index, 'name': param_name, 'type': type_param})

                if param_d.default != inspect.Parameter.empty:
                    fn_args[index]['default'] = param_d.default

            fn_datas['params'] = fn_args

            return fn_datas

    @staticmethod
    def init_inject(func: _C)-> _C:

        @wraps(func)
        def wrapper(*args, **kwargs)->Any:
            if 'is_inject' not in kwargs:
                fn_datas = ExtReflection.get_init_info_v1(func)
                new_args = list(args)

                for item in fn_datas['params']:
                    if item['name'] != 'self':
                        check_type = item['type']

                        if ResolveProviderFWDI.contains(check_type):
                            search_service = ResolveProviderFWDI.get_service(item['type'])
                            if search_service is not None:
                                new_args.append(search_service)

                return func(*new_args, **kwargs)
            else:
                new_args = {}
                for item in [item for item in kwargs if item != 'is_inject']:
                    element = {item:kwargs[item]}
                    new_args.update(element)

                return func(*args, **new_args)

        return wrapper
            
    @staticmethod
    def __get_default(lst_sign:list[inspect.Parameter], name_key:str) -> Any:
        search = Utilities.get_value_by_key(lst_sign, name_key)
        
        return search.default if search else None

    def __get_signature_args(fn:Callable[..., Any],fn_datas:dict = {})->list:
        return list(inspect.signature(fn.__wrapped__ if hasattr(fn, '__wrapped__') else fn).parameters.values())
    
    def __get_signature_has_self(fn_datas:dict)->bool:
        #fn_datas['signature_has_self'] = True if [item for item in fn_datas['method_signature'] if item.name == 'self'] else False
        return Utilities.check_key(fn_datas['method_signature'], 'self')
    
    def __fn_have_self(args:tuple, type_fn:type)->bool:
        result_1 = False

        if args:
            if isinstance(args[0], type_fn):
                result_1 = True
                
            if not isinstance(args[0], type):
                if issubclass(type(args[0]), type_fn):
                    result_1 = True

        if not result_1:
            result = False if not args else True if type(args[0]) == type_fn else False
        else:
            result = result_1
            
        return result

    @staticmethod
    def __get_inst_method_info_v2(fn:Callable[..., Any], args:tuple, kwargs:dict)->dict:
            fn_datas:dict = {}
            fn_args:list[dict] = []

            fn_datas['type'] = type(fn)
            fn_datas['origin_args'] = args
            fn_datas['origin_kwargs'] = kwargs
            fn_datas['method_signature'] = ExtReflection.__get_signature_args(fn, fn_datas)
            fn_datas['signature_has_self'] = ExtReflection.__get_signature_has_self(fn_datas)
            fn_datas['_arg_has_self_'] = ExtReflection.__fn_have_self(args, inspect._findclass(fn))
            
            if not fn_datas['_arg_has_self_']:
                raise Exception(f"Error function:{fn} dont have self arument !")
            
            fn_datas['full_args'] = True if len(args) == len(fn_datas['method_signature']) else False
            fn_datas['method_signature'] = fn_datas['method_signature'][1:]
                
            for param_name in fn_datas['method_signature']:
                type_param = param_name._annotation
                
                if hasattr(param_name, 'default') and param_name.default != inspect._empty:
                    fn_args.append({'name': param_name.name, 'type': type_param, 'default': param_name.default})
                else:
                    fn_args.append({'name': param_name.name, 'type': type_param})

            fn_datas['method_params'] = fn_args

            return fn_datas    

    @staticmethod
    def __get_static_method_info_v2(fn:Callable[..., Any], args:tuple, kwargs:dict)->dict:
            fn_datas:dict = {}
            fn_args:list[dict] = []

            fn_datas['type'] = type(fn)
            fn_datas['origin_args'] = args
            fn_datas['origin_kwargs'] = kwargs
            fn_datas['method_signature'] = ExtReflection.__get_signature_args(fn, fn_datas)

            if ExtReflection.__get_signature_has_self(fn_datas):
                raise Exception("Error in Static method has Self argument")

            if ExtReflection.__fn_have_self(args, inspect._findclass(fn)):
                fn_datas['origin_args'] = args[1:]
                
            for param_name in fn_datas['method_signature']:
                type_param = param_name._annotation
                
                if hasattr(param_name, 'default') and param_name.default != inspect._empty:
                    fn_args.append({'name': param_name.name, 'type': type_param, 'default': param_name.default})
                else:
                    fn_args.append({'name': param_name.name, 'type': type_param})

            fn_datas['method_params'] = fn_args

            return fn_datas    

    @staticmethod
    def __static_gen_new_args(info:dict)->dict:
        kwargs:dict = info['origin_kwargs']
        method_args:list[dict] = info['method_params']
        len_args = len(info['origin_args'])
        
        new_kwargs_params:dict[str, any] = {}

        if len_args > 0:
            method_args = method_args[len_args:]

        for item in method_args:
            arg_name, arg_type = item['name'], item['type']

            if arg_name in kwargs:
                try_get_value = kwargs.get(arg_name)
                new_kwargs_params[arg_name] = try_get_value
            else:
                if 'default' in item:
                    new_kwargs_params[arg_name] = item['default']
                elif ResolveProviderFWDI.contains(arg_type):
                    new_kwargs_params[arg_name] = ResolveProviderFWDI.get_service(arg_type)
                else:
                    raise Exception(f"Code::1000:Error type:{arg_type} not found in Dependency Collection and not in kwargs or default value.")

        return new_kwargs_params

    @staticmethod
    def __instance_gen_new_args(info:dict)->dict:
        args:tuple = info['origin_args']
        kwargs:dict = info['origin_kwargs']
        method_args:list[dict] = info['method_params']

        new_kwargs_params:dict[str, any] = {}
        len_args:int = len(args)
        
        if len_args > 1:
            shift_args = len_args - 1
            method_args = method_args[shift_args:]

        for item in method_args:
            arg_name, arg_type = item['name'], item['type']

            if arg_name in kwargs:
                try_get_value = kwargs.get(arg_name)
                new_kwargs_params[arg_name] = try_get_value
            else:
                if 'default' in item:
                    new_kwargs_params[arg_name] = item['default']
                elif ResolveProviderFWDI.contains(arg_type):
                    new_kwargs_params[arg_name] = ResolveProviderFWDI.get_service(arg_type)
                else:
                    raise Exception(f"code::1000:Error type:{arg_type} not found in Dependency Collection and not in kwargs or default value.")

        return new_kwargs_params

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------
    #------------------------------DECORATOR LOGGING INJECT
    #-----------------------------------------------------------------------------
    @staticmethod
    def _log_inject(func: _C)->Callable[..., Union[T, Awaitable[T]]]:
        
        @wraps(func)
        def __sync(*args, **kwargs):
            if ExtReflection.__log__ is None:
                ExtReflection.__log__ = ManagerLogging.get_logging("__inject__")

            match GlobalSettingService.log_lvl:
                case logging.DEBUG:
                    ExtReflection.__log__(f"sync exec :{func.__module__}::{func.__name__}, args={args}, kwargs:{kwargs}", 'debug')

            try:
                t_start = time.perf_counter_ns()

                result_call = func(*args, **kwargs)

                if GlobalSettingService.log_lvl == logging.DEBUG:
                    time_call = time.perf_counter_ns() - t_start
                    ExtReflection.__log__(f"run: {args} = duration time :{func.__name__}={time_call}")

                return result_call
            except Exception as ex:
                ExtReflection.__log__(f"sync exec :{func.__module__}::{func.__name__}, args={args}, kwargs:{kwargs}", 'error')               
                return None
    
        @wraps(func)
        async def __async(*args, **kwargs):
            if ExtReflection.__log__ is None:
                ExtReflection.__log__ = ManagerLogging.get_logging("__inject__")
                
            if GlobalSettingService.log_lvl == logging.DEBUG:
                ExtReflection.__log__(f"sync exec :{func.__module__}, {func.__name__}, args={args}")
            try:
                t_start = time.perf_counter_ns()
                
                result_call = await func(*args, **kwargs)
                
                if GlobalSettingService.log_lvl == logging.DEBUG:
                    time_call = time.perf_counter_ns() - t_start
                    ExtReflection.__log__(f"    duration time :{func.__name__}={time_call}")

                return result_call
            except Exception as ex:
                ExtReflection.__log__(f"error exec :{func.__name__}, Error:{ex},{args},{kwargs}", 'error')
                return None
        
        return __async if inspect.iscoroutinefunction(func) else __sync

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------
    #------------------------------INSTANCE SYNC METHOD INJECT
    #-----------------------------------------------------------------------------
    @_log_inject
    def _inject_inst_sync(func: _C)->Callable[..., Union[T, Awaitable[T]]]:
        ExtReflection.count_inject_sync += 1
        
        @wraps(func, updated=())
        def __inst_sync(*args, **kwargs)->T:
            
            if not ResolveProviderFWDI.is_init():
                return func(*args, **kwargs)
            
            if 'is_inject' not in kwargs:
                method_info = ExtReflection.__get_inst_method_info_v2(func, args, kwargs)
                length_param = len(method_info['method_params'])
                args = method_info['origin_args']
                kwargs = method_info['origin_kwargs']
                len_args = len(args)

                if method_info['_arg_has_self_'] and length_param == 0 or method_info['full_args']:
                    return func(*args)

                if kwargs and len(kwargs) == len(method_info['method_signature']):
                    return func(*args, **kwargs)


                if not method_info['signature_has_self'] and len_args == length_param:
                    return func(*args, **kwargs)
                elif method_info['signature_has_self'] and (len_args - 1) == length_param:
                    return func(*args, **kwargs)
                elif method_info['signature_has_self'] and len_args == 1 and length_param == 0:
                    return func(*args, **kwargs)

                new_args:dict = ExtReflection.__instance_gen_new_args(method_info)
                del method_info

                return func(*args, **new_args)
            else:
                if isinstance(kwargs, list):
                    new_args = [item for item in kwargs if item != 'is_inject']
                elif isinstance(kwargs, dict):
                    kwargs.pop('is_inject')
                    new_args = kwargs
                    
                return func(*args, **new_args)
        
        return __inst_sync
    #-----------------------------------------------------------------------------
    #------------------------------INSTANCE ASYNC METHOD INJECT
    #-----------------------------------------------------------------------------
    @_log_inject
    def _inject_inst_async(func: _C)->Callable[..., Union[T, Awaitable[T]]]:
        ExtReflection.count_inject_async += 1
        ExtReflection.__log__(f"async exec :{func.__module__}::{func.__name__}", 'debug')

        @wraps(func)
        async def __inst_async(*args, **kwargs)->T:

            if not ResolveProviderFWDI.is_init():
                return await func(*args, **kwargs)
            
            if 'is_inject' not in kwargs:
                method_info = ExtReflection.__get_inst_method_info_v2(func, args, kwargs)
                length_param = len(method_info['method_params'])
                args = method_info['origin_args']
                kwargs = method_info['origin_kwargs']
                len_args = len(args)
        
                if method_info['_arg_has_self_'] and length_param == 0:
                    return await func(*args)

                if kwargs and len(kwargs) == len(method_info['method_signature']):
                    return await func(*args, **kwargs)

                if not method_info['signature_has_self'] and len_args == length_param:
                    return await func(*args, **kwargs)
                elif method_info['signature_has_self'] and (len_args - 1) == length_param:
                    return await func(*args, **kwargs)
                elif method_info['signature_has_self'] and len_args == 1 and length_param == 0:
                    return await func(*args, **kwargs)

                new_args = ExtReflection.__instance_gen_new_args(method_info)

                return await func(*args, **new_args)
            else:
                new_args = [item for item in kwargs if item != 'is_inject']

                return await func(*args, **new_args)

        return __inst_async
    
    #-----------------------------------------------------------------------------
    #------------------------------STATIC SYNC METHOD INJECT
    #-----------------------------------------------------------------------------

    @_log_inject
    def _inject_static_sync(func: _C)->Callable[..., Union[T, Awaitable[T]]]:
        ExtReflection.count_inject_sync += 1

        @wraps(func, updated=())
        def __static_sync(*args, **kwargs)->T:

            if not ResolveProviderFWDI.is_init():
                return func(*args, **kwargs)
            
            if 'is_inject' not in kwargs:
                fn_signature = list(inspect.signature(func.__wrapped__ if hasattr(func, '__wrapped__') else func).parameters.values())

                if kwargs and len(kwargs) == len(fn_signature):
                    return func(**kwargs)

                method_info = ExtReflection.__get_static_method_info_v2(func, args, kwargs)
                args = method_info['origin_args']
                kwargs = method_info['origin_kwargs']
                length_param = len(method_info['method_params'])
                len_args = len(args)

                if len_args == length_param:
                    return func(*args, **kwargs)

                new_args:dict = ExtReflection.__static_gen_new_args(method_info)
                return func(*args, **new_args)
            else:
                new_args = [item for item in kwargs if item != 'is_inject']

                return func(*args, **new_args)
        
        return __static_sync
    
    #-----------------------------------------------------------------------------
    #------------------------------STATIC ASYNC METHOD INJECT
    #-----------------------------------------------------------------------------
    @_log_inject
    def _inject_static_async(func: _C)->Callable[..., Union[T, Awaitable[T]]]:
        ExtReflection.count_inject_async += 1

        @wraps(func, updated=())
        async def __static_async(*args, **kwargs)->T:

            if not ResolveProviderFWDI.is_init():
                return await func(*args, **kwargs)
            
            if 'is_inject' not in kwargs:
                fn_signature = list(inspect.signature(func.__wrapped__ if hasattr(func, '__wrapped__') else func).parameters.values())

                if kwargs and len(kwargs) == len(fn_signature):
                    return await func(**kwargs)

                method_info = ExtReflection.__get_static_method_info_v2(func, args, kwargs)
                args = method_info['origin_args']
                kwargs = method_info['origin_kwargs']
                length_param = len(method_info['method_params'])
                len_args = len(args)

                if len_args == length_param:
                    return await func(*args, **kwargs)

                new_args = ExtReflection.__static_gen_new_args(method_info)

                return await func(*args, **new_args)
            else:
                new_args = [item for item in kwargs if item != 'is_inject']

                return await func(*args, **new_args)
        
        return __static_async

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    
    @staticmethod
    def is_class(obj:type[TService]|TService)->bool:
        return True if isinstance(obj, type) else False
    
    @staticmethod
    def is_injectable_init(obj)->bool:
        return True if '__init__' in obj.__dict__ else False