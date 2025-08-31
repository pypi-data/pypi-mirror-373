from abc import ABCMeta, abstractmethod
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from ...Application.DTO.Auth.user_in_db import UserInDB
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.DTO.Auth.model_user import User
from ...Utilites.jwt_tools_static import JwtToolsFWDI


class BaseAuthServiceFWDI(metaclass=ABCMeta):
    oauth2_scheme:OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")

    @abstractmethod
    def get_user(username: str, 
                    db_context:BaseUserRepositoryFWDI, 
                    jwt_tools:JwtToolsFWDI)->UserInDB|None:    
        ...

    @abstractmethod
    def authenticate_user(db_context:BaseUserRepositoryFWDI, 
                          username: str, 
                          password: str, 
                          jwt_tools:JwtToolsFWDI)->UserInDB|None:
        ...

    @abstractmethod
    def get_current_user(security_scopes: SecurityScopes, 
                         token: Annotated[str, Depends(oauth2_scheme)], 
                         jwt_tools:JwtToolsFWDI=Depends())->UserInDB|None:
        ...
    
    @abstractmethod
    def get_current_active_user(current_user:User = Security(get_current_user),)->UserInDB|None:
        ...