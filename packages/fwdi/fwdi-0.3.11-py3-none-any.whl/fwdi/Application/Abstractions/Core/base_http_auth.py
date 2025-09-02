from abc import ABC, abstractmethod

class BaseHttpAuth(ABC):

    @abstractmethod
    def login(username:str, 
              password:str)->tuple[bool, str]:
        ...