import multiprocessing
from fastmcp.server.server import Transport
from fastmcp.server.auth.providers.jwt import JWTVerifier

from ...Infrastructure.MCP.mcp_service import MCPService
from ...Application.Abstractions.base_mcp_service import BaseMCPService
from ...Application.Abstractions.base_manager_mcp_service import BaseManagerMCPService


class ManagerMCPService(BaseManagerMCPService):
    def __init__(self):
        super().__init__()
    
    def add_service(self, name:str, instructions:str, host:str='0.0.0.0', port:int=5000, jwt_provider:JWTVerifier|None=None)->BaseMCPService:
        new_instance:BaseMCPService = MCPService.from_param(name=name, 
                                                            instructions=instructions,
                                                            host=host,
                                                            port=port,
                                                            jwt_provider=jwt_provider
                                                            )
        self._service_collection[name] = new_instance
        return new_instance
    
    def count(self)->int:
        return len(self._service_collection)

    def __getitem__ (self, name:str)->BaseMCPService|None:
        if name in self._service_collection:
            return self._service_collection[name]
        else:
            return None
    
    def run_all(self, mcp_servers:list[dict]={}):
        for msp_server in mcp_servers:
            self._service_collection[msp_server['name']].run(transport=msp_server['transport'])

    def run_old(self, transport:Transport='streamable-http'):
        for name in self._service_collection.keys():
            self._service_collection[name].run(transport=transport)

    def run(self, transport:Transport='streamable-http'):
        
        lst_proccess:list[multiprocessing.Process] = []
        for name in self._service_collection.keys():
            tmp_proccess = multiprocessing.Process(target=self._service_collection[name].run, kwargs={'transport': transport})
            lst_proccess.append(tmp_proccess)

        for p in lst_proccess:        
            p.start()

        for p in lst_proccess:
            p.join()