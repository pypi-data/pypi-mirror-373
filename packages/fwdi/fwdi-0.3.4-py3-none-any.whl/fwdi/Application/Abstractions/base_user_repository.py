from abc import ABCMeta, abstractmethod

from .base_manager_context import BaseManagerContextFWDI

class BaseUserRepositoryFWDI(metaclass=ABCMeta):
    
    @abstractmethod
    def get_all(self, manager_db_context: BaseManagerContextFWDI)->list[dict]:
        ...

    @abstractmethod
    def get_user_scopes(self, email:str, manager_db_context: BaseManagerContextFWDI)->list[str]|None:
        ...