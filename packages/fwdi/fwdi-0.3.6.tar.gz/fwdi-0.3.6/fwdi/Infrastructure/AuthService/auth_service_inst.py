from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError

from pydantic import ValidationError

from fwdi.Utilites.jwt_tools_inst import JwtToolsV2FWDI

from ...Application.Abstractions.base_jwt_tools_v2 import BaseJwtToolsV2FWDI
from ...Application.Abstractions.base_jwt_service_instance import BaseAuthServiceV2FWDI
from ...Application.DTO.Auth.user_in_db import UserInDB
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.DTO.Auth.model_user import User
from ...Application.DTO.Auth.token_data import TokenData
from ...Persistence.manager_db_context import ManagerDbContextFWDI


class AuthServiceV2FWDI(BaseAuthServiceV2FWDI):

    def get_user(self, 
                    username: str, 
                    db_context:BaseUserRepositoryFWDI, 
                    jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            AuthServiceV2FWDI.__log__(f"{__name__}, User not found:{username}")
            return None
        
        return user

    def authenticate_user(self, 
                          db_context:BaseUserRepositoryFWDI, 
                          username: str, 
                          password: str, 
                          jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            AuthServiceV2FWDI.__log__(f"{__name__}, User not found:{username}")
            return None
        
        if not jwt_tools.verify_password(password, user.hashed_password):
            AuthServiceV2FWDI.__log__(f"{__name__}, User not authentificate:{username}:{password}")
            return None
        
        AuthServiceV2FWDI.__log__(f"{__name__}, Authentificate:{user}", "debug")
        
        return user
    
    def get_current_user(self, 
                         security_scopes: SecurityScopes, 
                         token: Annotated[str, Depends(BaseAuthServiceV2FWDI.oauth2_scheme)], 
                         jwt_tools:JwtToolsV2FWDI=Depends())->UserInDB|None:
        
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            payload = jwt_tools.decode_payload_token(token)
            username: str = payload.get("sub")
            email: str = payload.get("email")
            
            if username is None:
                AuthServiceV2FWDI.__log__(f"{__name__}, Could not validate credentials:{payload}")
                raise credentials_exception
            
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username, email=email)
        except (InvalidTokenError, ValidationError) as ex:
            AuthServiceV2FWDI.__log__(f"Error:{ex}", 'error')
            raise credentials_exception
        
        managerdb = ManagerDbContextFWDI()
        users_db = managerdb.get_metadata_user()
        user = jwt_tools.get_user_by_email(users_db, email=token_data.email)
        
        if user is None:
            AuthServiceV2FWDI.__log__(f"User not found :{users_db}", 'error')
            raise credentials_exception
        
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                AuthServiceV2FWDI.__log__(f"user:{user}, Not enough permissions")

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return user
    
    def get_current_active_user(self, 
                                current_user:User = Security(get_current_user))->UserInDB|None:
        if current_user.disabled:
            AuthServiceV2FWDI.__log__(f"{__name__}, 400: Inactive user")
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return current_user