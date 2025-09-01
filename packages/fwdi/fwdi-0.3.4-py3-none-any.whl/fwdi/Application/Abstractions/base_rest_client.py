from abc import ABCMeta, abstractmethod
from pydantic import BaseModel

class BaseRestClientFWDI(metaclass=ABCMeta):
    
    @property
    @abstractmethod
    def IsAuth(self):
        ...

    @abstractmethod
    def init(self, config:any):
        ...
    @abstractmethod
    def login(self, url:str='/token')->bool:
        ...
    
    @abstractmethod
    def get(self, path:str, model:BaseModel=None)->tuple|None:
        ...

    @abstractmethod
    def post(self, path:str, model:BaseModel)->tuple|None:
        ...