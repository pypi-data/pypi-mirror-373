import inspect
from uuid import uuid4
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union
from fwdi.Utilites.waitable_event import WaitableEvents

_T = TypeVar('_T')

class JobTask():
    def __init__(self, 
                 fn: Callable[..., Union[Callable, Coroutine]], 
                 args:list, 
                 id:str = '',
                 fn_callback: Callable[..., Union[Callable, Coroutine]] | None=None,
                 param_callback: dict | None=None) -> None:
        
        self.id:str = str(uuid4()) if not id else id
        self.__fn:Optional[Callable[..., Union[Callable,Coroutine[Any, Any, Any]]]] = fn
        self.__args:dict = args
        self.__event:WaitableEvents = WaitableEvents()
        self.__callback_result:Optional[Callable[..., Union[Callable,Coroutine[Any, Any, Any]]]] = fn_callback
        self.__param_callback:dict|None = param_callback

    def is_callback(self)->bool:
        return True if self.__callback_result is not None else False

    async def async_call(self)->any:
        try:
            if inspect.iscoroutinefunction(self.__fn):
                result = await self.__fn(**self.__args)
                return result
            else:
                result = self.__fn(**self.__args)
                return result
            
        except Exception as ex:
            JobTask.__log__(f"Error : JobTask->call: {ex}", "error")
            return result

    def callback_result(self, result:_T):
        try:
            self.__callback_result(self.__param_callback, result)

        except Exception as ex:
            JobTask.__log__(f"Error : JobTask->callback_result: {ex}", "error")

    def set_result(self, result:any):
        JobTask.__log__(f"Set result:{result}", "debug")
        self.__event.set(result)

    def wait_result(self)->_T:
        ret, result = self.__event.wait()
        
        return result if ret else None
    
    def __repr__(self):
        return f"fnc:{self.__fn}, args:{self.__args}"
    
    def __str__(self):
        return f"fnc:{self.__fn}, args:{self.__args}"