from typing import Awaitable, Callable, TypeVar, Union
T = TypeVar('T')

class BrokerEvent:
    def __init__(self, name:str):
        self.name:str = name
        self._handlers:list = []

    def __iadd__(self, handler:Callable[..., Union[T, Awaitable[T]]]):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler:Callable[..., Union[T, Awaitable[T]]]):
        self._handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self._handlers:
            return handler(*args, **kwargs)