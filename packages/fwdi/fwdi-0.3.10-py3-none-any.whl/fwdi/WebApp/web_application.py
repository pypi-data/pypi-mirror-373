#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import uvicorn
from typing import Callable, Any, TypeVar
from fastapi import FastAPI
import gradio as gr
from fastmcp.prompts.prompt import PromptResult
from fastapi.middleware.cors import CORSMiddleware
from collections.abc import Awaitable

from ..Application.Logging.manager_logging import ManagerLogging
from ..Utilites.ext_global_setting import ExtGlobalSetting
from ..Domain.Configure.global_setting_service import GlobalSettingService
from ..Application.DependencyInjection.resolve_provider import ResolveProviderFWDI
from ..Application.Abstractions.Core.base_controller import BaseControllerFWDI

T = TypeVar('T', bound='WebApplication')

class WebApplication():
    def __init__(self, config:GlobalSettingService = None, **kwargs):
        from ..Application.Logging.manager_logging import ManagerLogging
        from .web_application_builder import WebApplicationBuilder
        from ..Application.Abstractions.External.base_mcp_service import BaseMCPService
                
        if config is None:
            config = GlobalSettingService
        
        self._config:GlobalSettingService = config
        self.__log__ = ManagerLogging.get_logging('WebApplication', self._config) #SysLogging(logging_level=TypeLogging.DEBUG, filename='WebApplication')
        
        self.__log__(f"{__name__}:{kwargs}")
        self.__rest_app:FastAPI|None = None
        self.__mcp_instance:BaseMCPService|None = None
        self.instance:'WebApplicationBuilder' = None
        
        self.resolver:ResolveProviderFWDI = None
        self.Name:str = kwargs['name'] if 'name' in kwargs else ''

    @property
    def Debug(self)->bool:
        return self.__debug

    @property
    def app(self)->FastAPI:
        return self.__rest_app

    def set_mcp(self, inst):
        self.__mcp_instance = inst

    def has_mcp(self)->bool:
        return True if self.__mcp_instance else False
    
    def mount_mcp(self, path:str='/'):
        app_mcp = self.__mcp_instance.get_http_app()
        self.__rest_app.mount(path, app_mcp)

    def update_cors(self, 
                    origins:list[str], 
                    allow_credentials:bool, 
                    allow_methods:list[str], 
                    allow_headers:list[str]):
        try:
            self.__rest_app.add_middleware(
                                CORSMiddleware,
                                allow_origins=origins,  # List of allowed origins
                                allow_credentials=allow_credentials,  # Allow credentials (cookies, authorization headers)
                                allow_methods=allow_methods,  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
                                allow_headers=allow_headers,  # Allow all headers
                            )
            return True
        except Exception as ex:
            self.__log__(f"ERROR:{ex}", 'error')
            return False

    def map_controller(self, controller:BaseControllerFWDI)->None:
        self.__log__(f"{__name__}:{controller}")
        if hasattr(controller, "routes"):
            self.__rest_app.include_router(controller)
        else:
            raise Exception(f"{controller} has no have attribute routes !")

    def add_web_page(self, inst: gr.Blocks, path:str="/panel", is_auth:bool=False, allowed_paths:list[str]=None):
        from ..Presentation.DefaultControllers.http_auth import HttpAuthFWDI

        self.__log__(f"{__name__}:{path}:{inst}", 'debug')
        if not is_auth:
            self.__rest_app = gr.mount_gradio_app(self.__rest_app, inst, path=path, allowed_paths=allowed_paths, favicon_path='icons')
        else:
            self.__rest_app = gr.mount_gradio_app(self.__rest_app, inst, path=path, auth=HttpAuthFWDI.login, allowed_paths=allowed_paths, favicon_path='icons')
    
    def map_route(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__rest_app.add_route(path=path, route=endpoint)

    def map_get(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__rest_app.add_api_route(path=path, endpoint=endpoint, methods=["GET"])
    
    def map_post(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__rest_app.add_api_route(path=path, endpoint=endpoint, methods=["POST"])

    def map_delete(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__rest_app.add_api_route(path=path, endpoint=endpoint, methods=["DELETE"])

    def map_put(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__rest_app.add_api_route(path=path, endpoint=endpoint, methods=["PUT"])
    
    def create_fast_api(self, with_mcp:bool=False, generic_mcp_path:str='/'):
        if with_mcp:
            if self.__mcp_instance:
                lifespan = self.__mcp_instance.get_http_app(generic_mcp_path).lifespan
                self.__rest_app = FastAPI(title=self._config.name, description=self._config.description, lifespan=lifespan)
            else:                
                self.__rest_app = FastAPI(title=self._config.name, description=self._config.description)
        else:
            self.__mcp_instance = None
            self.__rest_app = FastAPI(title=self._config.name, description=self._config.description)

    def add_tool(self, 
                 fn_tool:Callable[..., Any], 
                 description:str, 
                 tags:set[str]=str(), 
                 name:str=str(), 
                 title:str=str()):
        if not self.__mcp_instance:
            raise Exception("Instance MCP server not create")
        
        self.__mcp_instance.add_tool(fn_tool=fn_tool, 
                                    description=description, 
                                    tags=tags, 
                                    name=name, 
                                    title=title)
    
    def add_prompt(self, fn_tool:Callable[..., PromptResult | Awaitable[PromptResult]], description:str, tags:set[str]=str(), name:str=str(), title:str=str()):
        if not self.__mcp_instance:
            raise Exception("Instance MCP server not create")

        self.__mcp_instance.add_prompt(fn_tool=fn_tool, 
                                        description=description, 
                                        tags=tags, 
                                        name=name, 
                                        title=title)
        
    def add_resource(self, fn_tool:Callable[..., Any], uri:str, description:str, tags:set[str]=str(), name:str=str(), title:str=str()):
        if not self.__mcp_instance:
            raise Exception("Instance MCP server not create")

        self.__mcp_instance.add_resource(fn_tool=fn_tool,
                                        uri=uri,
                                        description=description, 
                                        tags=tags, 
                                        name=name, 
                                        title=title)
    def add_health_checks(self):
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        DependencyInjectionPresentation.AddHealthChecks(self)

    def add_redirect_root_page(self, new_url:str):
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        DependencyInjectionPresentation.AddRedirectRootPage(self, new_url)


    @classmethod
    def create_builder(cls:type[T], **kwargs):
        from .web_application_builder import WebApplicationBuilder
        ExtGlobalSetting.load('service_config.json')

        __log__ = ManagerLogging.get_logging('WebApplicationBuilder', GlobalSettingService)
        
        webapp_instance = cls(GlobalSettingService, **kwargs)
        webapp_instance.instance = WebApplicationBuilder(webapp_instance)
        
        return webapp_instance.instance
    
    def __run_rest(self, **kwargs):
        self.__log__(f"Run service:{__name__}:{kwargs}")
        if not kwargs:
            if GlobalSettingService.ssl_keyfile and GlobalSettingService.ssl_certfile:
                uvicorn.run(self.__rest_app, 
                            host=GlobalSettingService.current_host, 
                            port=GlobalSettingService.current_port, 
                            ssl_keyfile=GlobalSettingService.ssl_keyfile,
                            ssl_certfile=GlobalSettingService.ssl_certfile,
                            ssl_keyfile_password=GlobalSettingService.ssl_keyfile_password,
                            )
            else:
                uvicorn.run(self.__rest_app, host=GlobalSettingService.current_host, port=GlobalSettingService.current_port)
        else:
            GlobalSettingService.current_host = kwargs.get('host', 'localhost')
            GlobalSettingService.current_port = kwargs.get('port', 5000)
            GlobalSettingService.ssl_keyfile = kwargs.get('ssl_keyfile', "")
            GlobalSettingService.ssl_certfile = kwargs.get('ssl_certfile', "")
            GlobalSettingService.ssl_keyfile_password = kwargs.get('ssl_keyfile_password', "")
            
            # ssl_keyfile="/etc/letsencrypt/live/my_domain/privkey.pem", 
            # ssl_certfile="/etc/letsencrypt/live/my_domain/fullchain.pem"
            
            # ssl_keyfile="./key.pem",
            # ssl_certfile="./cert.pem",
            
            # ssl_keyfile="/path/to/your/private.key",
            # ssl_certfile="/path/to/your/certificate.crt"

            uvicorn.run(self.__rest_app, **kwargs)
    
    def run(self, **kwargs):
        self.__run_rest(**kwargs)