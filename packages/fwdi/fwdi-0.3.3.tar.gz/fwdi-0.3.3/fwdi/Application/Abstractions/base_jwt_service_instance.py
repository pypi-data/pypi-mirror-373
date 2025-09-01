from abc import ABCMeta, abstractmethod
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from ...Application.DTO.Auth.user_in_db import UserInDB
from ...Application.DTO.Auth.model_user import User

from ...Application.Abstractions.base_jwt_tools_v2 import BaseJwtToolsV2FWDI
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI


class BaseAuthServiceV2FWDI(metaclass=ABCMeta):
    oauth2_scheme:OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")

    @abstractmethod
    def get_user(self, username: str, 
                    db_context:BaseUserRepositoryFWDI, 
                    jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:    
        ...

    @abstractmethod
    def authenticate_user(self, db_context:BaseUserRepositoryFWDI, 
                          username: str, 
                          password: str, 
                          jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:
        ...

    @abstractmethod
    def get_current_user(self, security_scopes: SecurityScopes, 
                         token: Annotated[str, Depends(oauth2_scheme)], 
                         jwt_tools:BaseJwtToolsV2FWDI=Depends())->UserInDB|None:
        ...
    
    @abstractmethod
    def get_current_active_user(self, current_user:User = Security(get_current_user),)->UserInDB|None:
        ...