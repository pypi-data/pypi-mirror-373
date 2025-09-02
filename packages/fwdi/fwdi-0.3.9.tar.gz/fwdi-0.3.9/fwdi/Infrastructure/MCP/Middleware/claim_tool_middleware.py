from typing import Any
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.middleware import CallNext
from fastmcp.server.dependencies import get_http_request
from fastmcp.exceptions import ToolError

from ....Utilites.jwt_tools_static import JwtToolsFWDI
from ....Application.Abstractions.External.base_mcp_service import BaseMCPService

class ClaimsToolsMiddleware(Middleware):
    def __init__(self, instance:BaseMCPService):
        super().__init__()
        self.__instance:BaseMCPService = instance

    async def on_call_tool(self, context:MiddlewareContext, call_next:CallNext[Any, Any]):
        if context.fastmcp_context:
            tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
            token = JwtToolsFWDI.get_token(get_http_request())
            if token:
                public_key:str = self.__instance.get_config_key('public_key')
                algorithms:str = self.__instance.get_config_key('algorithms')
                user_claims = JwtToolsFWDI.decode_token(token, public_key, algorithms)
            
            if user_claims:
                if tool.tags:
                    intersec_claim = tool.tags.intersection(user_claims['scope'])
                    if not intersec_claim:
                        raise ToolError("Access denied: no access claims")
 
            if not tool.enabled:
                raise ToolError("Tool is currently disabled")
        
        return await call_next(context)