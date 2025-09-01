from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseBrokerClient(ABC):
    def __init__(self, name_queue:str, host:str='localhost', port:int=5672):
        ...
    
    @abstractmethod
    def stop(self):
        ...
    
    @abstractmethod
    def to_reply(self, model:BaseModel, to_back_queue:str, command_id:int=2)->bool:
        ...
    
    @abstractmethod
    def is_queue_exists(name_queue:str, host:str, port:int, credential:dict={})->bool:
        ...

    @abstractmethod
    def to_publish(self, model:BaseModel)->bool:
        ...