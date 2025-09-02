#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from typing import TypeVar
from fastapi.security import OAuth2PasswordBearer

from ..Infrastructure.MCP.mcp_service import MCPService
from ..Persistence.default_init_db import DefaultInitializeDB
from ..Application.Logging.manager_logging import ManagerLogging
from ..Application.Abstractions.External.base_service_collection import BaseServiceCollectionFWDI
from ..Application.DependencyInjection.resolve_provider import ResolveProviderFWDI
from ..Application.DependencyInjection.service_collection import ServiceCollectionFWDI
from ..Application.Abstractions.Core.base_jwt_service_instance import BaseAuthServiceV2FWDI
from ..Application.Abstractions.Core.base_jwt_service import BaseAuthServiceFWDI

T = TypeVar('T')

class WebApplicationBuilder():
    def __init__(self, web_app_inst:T) -> None:
        from fwdi.WebApp.web_application import WebApplication
        self.__log__ = ManagerLogging.get_logging('WebApplicationBuilder', web_app_inst._config)
        self.__log__(f"{__name__}:{web_app_inst}")
        self.__instance_app:WebApplication = web_app_inst
        self.services:BaseServiceCollectionFWDI = ServiceCollectionFWDI()
        
        self.__scopes:dict[str, str] = {}
        self.__is_build:bool = False

    def build(self, with_mcp:bool=False)-> type[T]:
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        from ..Utilites.dependency_injection import DependencyInjection as DependencyInjectionUtilites

        if self.__is_build:
            raise Exception('Error is already build.')
        
        self.__log__(f"Build services")
        
        self.__instance_app.create_fast_api(with_mcp)
        self.__instance_app.instance = self
        self.__instance_app.resolver = ResolveProviderFWDI(self.services.GenerateContainer())
        
        #---------------------- DEFAULT WEB CONTROLLER SERVICES ------------------------------------
        #----------------------DEFAULT SERVICES DEPENDENCY------------------------------------
        from ..Persistence.dependency_injection import DependencyInjection as PersistenceDependencyInjection
        self.__instance_app.__log__(f"Create dependency injection Persistence")
        PersistenceDependencyInjection.AddPersistence(self.__instance_app.instance.services)

        self.__instance_app.__log__(f"Create dependency injection Application")
        from ..Application.dependency_injection import DependencyInjection as ApplicationDependencyInjection
        ApplicationDependencyInjection.AddApplication(self.__instance_app.instance.services)

        self.__instance_app.__log__(f"Create dependency injection Infrastructure")
        from ..Infrastructure.dependency_injection import DependencyInjection as InfrastructureDependencyInjection
        InfrastructureDependencyInjection.AddInfrastructure(self.__instance_app.instance.services)
        
        from ..Presentation.dependency_injection import DependencyInjection as PresentationDependencyInjection
        PresentationDependencyInjection.AddPresentation(self.__instance_app.instance.services)
        
        #----------------------/DEFAULT SERVICES DEPENDENCY-----------------------------------        
        self.__log__(f"Create dependency injection Utilites")
        DependencyInjectionUtilites.AddUtilites(self.services)
        self.__log__(f"Create dependency injection Presentation")
        DependencyInjectionPresentation.AddEndpoints(self.__instance_app)
        
        #---------------------- /DEFAULT WEB CONTROLLER SERVICES -----------------------------------
        self.__log__(f"Inititalize OAuth2PasswordBearer: scope:{self.__scopes}")
        BaseAuthServiceV2FWDI.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=self.__scopes,) if len(self.__scopes) > 0 else OAuth2PasswordBearer(tokenUrl="token")
        BaseAuthServiceFWDI.oauth2_scheme = BaseAuthServiceV2FWDI.oauth2_scheme
        self.__log__(f"Inititalize DB")
        DefaultInitializeDB.init_db(self.__scopes)
        self.__is_build = True
        
        return self.__instance_app
    
    def add_scope(self, scopes:dict[str,str]):
        if self.__is_build:
            raise Exception('Error add dependency after build')
        
        for item in scopes.items():
            if not item in self.__scopes:
                self.__scopes[item[0]] = item[1]
    
    def create_mcp(self, name:str, instructions:str|None=None, jwt_verifier:dict={}):
        mcp_instance = MCPService.from_param(name=name, 
                                                instructions=instructions,
                                                jwt_virifier=jwt_verifier,
                                                )
        self.__instance_app.set_mcp(mcp_instance)