from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any, Callable

from fastmcp.server.server import Transport
from fastmcp.prompts.prompt import Prompt, PromptResult

class BaseMCPService(ABC):

    @abstractmethod
    def add_tool(self, 
                 fn_tool:Callable[..., Any], 
                 description:str, 
                 tags:set[str], 
                 name:str=str(), 
                 title:str=str()):
        ...
    
    @abstractmethod
    def add_resource(self, 
                     fn_tool:Callable[..., Any], 
                     uri:str, 
                     description:str, 
                     tags:set[str], 
                     name:str=str(), 
                     title:str=str()):
        ...
    
    @abstractmethod
    def add_prompt(self, 
                   fn_tool:Callable[..., PromptResult | Awaitable[PromptResult]], 
                   description:str, 
                   tags:set[str], 
                   name:str=str(), 
                   title:str=str()):
        ...
    
    @abstractmethod
    def run(self, transport:Transport='streamable-http'):
        ...