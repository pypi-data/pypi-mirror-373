from typing import NamedTuple

from fastmcp.server.auth.auth import OAuthProvider, AccessToken
from mcp.server.auth.provider import AuthorizationParams, AuthorizationCodeT, RefreshTokenT, AccessTokenT
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

class OAuthClientStruct(NamedTuple):
    Client:OAuthClientInformationFull
    AccessToken:str
    RefreshToken:str
    AuthorizationCode:str

class SelfOAuthProvider(OAuthProvider):
    def __init__(self, *, base_url, 
                            issuer_url = None, 
                            service_documentation_url = None, 
                            client_registration_options = None, 
                            revocation_options = None, 
                            required_scopes = None, 
                            resource_server_url = None):
        super().__init__(base_url=base_url, 
                         issuer_url=issuer_url, 
                         service_documentation_url=service_documentation_url, 
                         client_registration_options=client_registration_options, 
                         revocation_options=revocation_options, 
                         required_scopes=required_scopes, 
                         resource_server_url=resource_server_url)
        
        self.__lst_client:dict[str, OAuthClientStruct] = {}
    
    def get_client(self, client_id:str)->OAuthClientInformationFull|None:
        if client_id in self.__lst_client:
            return self.__lst_client[client_id].Client
        
        return None
    
    def register_client(self, client_info:OAuthClientInformationFull)->None:
        if client_info.client_id not in self.__lst_client:
            self.__lst_client[client_info.client_id] = OAuthClientStruct(Client=client_info, 
                                                                         AccessToken="",
                                                                         RefreshToken="",
                                                                         Token="")

    def authorize(self, client:OAuthClientInformationFull, params:AuthorizationParams):
        return super().authorize(client, params)
   
    
    def load_authorization_code(self, client:OAuthClientInformationFull, authorization_code:str)->AuthorizationCodeT | None:
        return super().load_authorization_code(client, authorization_code)
    
    def exchange_authorization_code(self, client:OAuthClientInformationFull, authorization_code:AuthorizationCodeT)->OAuthToken:
        return super().exchange_authorization_code(client, authorization_code)
    
    def load_refresh_token(self, client:OAuthClientInformationFull, refresh_token:str)->RefreshTokenT|None:
        return super().load_refresh_token(client, refresh_token)
    
    def exchange_refresh_token(self, 
                               client:OAuthClientInformationFull, 
                               refresh_token:RefreshTokenT, 
                               scopes:list[str])->OAuthToken:
        return super().exchange_refresh_token(client, refresh_token, scopes)
    
    def load_access_token(self, token:str)->AccessTokenT|None:
        return super().load_access_token(token)
    
    def revoke_token(self, token:AccessTokenT | RefreshTokenT)->None:
        return super().revoke_token(token)
    
    def verify_token(self, token:str)->AccessToken|None:
        return super().verify_token(token)