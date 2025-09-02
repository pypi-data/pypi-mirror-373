from abc import ABC, abstractmethod
from fastmcp.server.server import Transport

from ...Application.Abstractions.base_mcp_service import BaseMCPService

class BaseManagerMCPService(ABC):
    def __init__(self):
        super().__init__()
        self._service_collection:dict[str, BaseMCPService] = {}
    
    @abstractmethod
    def count(self)->int:
        ...

    @abstractmethod
    def add_service(self, name:str, instructions:str, host:str='0.0.0.0', port:int=5000)->BaseMCPService:
        ...
    
    @abstractmethod
    def __getitem__ (self, name:str)->BaseMCPService|None:
        ...
    
    @abstractmethod
    def run_all(self, mcp_servers:list[dict]={}):
        ...
    
    @abstractmethod
    def run(self, transport:Transport='streamable-http'):
        ...