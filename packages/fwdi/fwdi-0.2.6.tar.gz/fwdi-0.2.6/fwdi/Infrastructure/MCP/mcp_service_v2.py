from collections.abc import Awaitable
from typing import Any, Callable
from fastmcp import FastMCP
from fastmcp.server.server import Transport
from fastmcp.resources.resource import Resource
from fastmcp.prompts.prompt import Prompt, PromptResult
from fastmcp.tools import Tool
from fastmcp.server.auth.providers.jwt import JWTVerifier
from ...Application.Abstractions.base_mcp_service import BaseMCPService


class MCPService(BaseMCPService):
    def __init__(self):
        self.__host:str = '0.0.0.0'
        self.__port:int = '5000'
        self.__name:str = 'MCPServer'
        self.__instructions:str = ''
        self.__mcp:FastMCP|None = None
        self.__lst_tool:list[Tool] = []
        self.__lst_resource:list[Tool] = []
        self.__lst_prompt:list[Tool] = []
        self.__auth:JWTVerifier|None = None

    @classmethod
    def from_param(cls, name:str, instructions:str, host:str='0.0.0.0', port:int=5000)->'MCPService':
        new_instance:'MCPService' = cls()
        new_instance.__host = host
        new_instance.__port = port
        new_instance.__name = name
        new_instance.__instructions = instructions
        new_instance.__mcp = FastMCP(name=name, instructions=instructions, host=host, port=port)

        return new_instance
        
    def add_tool(self, fn_tool:Callable[..., Any], description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Tool.from_function(fn=fn_tool, name=name, title=title, description=description, tags=tags)
            self.__lst_tool.append(self.__mcp.add_tool(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_tool):{ex}")

    def add_resource(self, fn_tool:Callable[..., Any], uri:str, description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Resource.from_function(fn=fn_tool, uri=uri, name=name, title=title, description=description, tags=tags)
            self.__lst_resource.append(self.__mcp.add_resource(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_resource):{ex}")

    def add_prompt(self, fn_tool:Callable[..., PromptResult | Awaitable[PromptResult]], description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Prompt.from_function(fn=fn_tool, name=name, title=title, description=description, tags=tags)
            self.__lst_prompt.append(self.__mcp.add_prompt(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_prompt):{ex}")

    def run(self, transport:Transport='streamable-http'):
        self.__mcp.run(transport=transport)