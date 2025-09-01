import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Application.Abstractions.base_jwt_tools_v2 import BaseJwtToolsV2FWDI
from ...Utilites.jwt_tools_inst import JwtToolsV2FWDI
from ...Application.Abstractions.base_jwt_service import BaseAuthServiceFWDI
from ...Application.DTO.Auth.user_in_db import UserInDB
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.DTO.Auth.model_user import User
from ...Application.DTO.Auth.token_data import TokenData
from ...Persistence.manager_db_context import ManagerDbContextFWDI


class AuthServiceFWDI(BaseAuthServiceFWDI):

    @staticmethod
    def get_user(username: str, 
                    db_context:BaseUserRepositoryFWDI, 
                    jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, db context:{db_context}, username:{username}", 'debug')

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            return None
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, Authentificate:{user}", "debug")
        
        return user

    @staticmethod
    def authenticate_user(db_context:BaseUserRepositoryFWDI, 
                          username: str, 
                          password: str, 
                          jwt_tools:BaseJwtToolsV2FWDI)->UserInDB|None:
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"authenticate_user {__name__}, db context:{db_context}, username:{username}, pass:{password}", "debug")

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            return None
        
        if not jwt_tools.verify_password(password, user.hashed_password):
            return None
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, Authentificate:{user}", "debug")
        
        return user
    
    @staticmethod
    def get_current_user(security_scopes: SecurityScopes, 
                         token: Annotated[str, Depends(BaseAuthServiceFWDI.oauth2_scheme)], 
                         jwt_tools: JwtToolsV2FWDI=Depends(),
                         managerdb: ManagerDbContextFWDI=Depends())->UserInDB|None:
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, SecurityScopes:{security_scopes}:{token}")
        
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, authenticate_value:{authenticate_value}")

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        user_not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            payload = jwt_tools.decode_payload_token(token)

            if GlobalSettingService.log_lvl == logging.DEBUG:
                AuthServiceFWDI.__log__(f"{__name__}, payload:{payload}", 'debug')
            
            username: str = payload.get("sub")
            email: str = payload.get("email")
            
            if username is None:
                raise credentials_exception
            
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username, email=email)
            
        except (InvalidTokenError, ValidationError) as ex:
            AuthServiceFWDI.__log__(f"Error:{ex}", 'error')
            raise credentials_exception
        
        users_db = managerdb.get_metadata_user()
        if not users_db:
            raise Exception(f"Error managerdb.get_metadata_user")
        
        if user := jwt_tools.get_user_by_email(users_db, email=token_data.email):
            if GlobalSettingService.log_lvl == logging.DEBUG:
                AuthServiceFWDI.__log__(f"{__name__}: Found user in account db by email: {token_data.email}", "debug")
        else:
            if GlobalSettingService.log_lvl == logging.DEBUG:
                AuthServiceFWDI.__log__(f"User not found :{users_db}", 'debug')

            raise user_not_found_exception
        
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                if GlobalSettingService.log_lvl == logging.DEBUG:
                    AuthServiceFWDI.__log__(f"user:{user}, Not enough permissions", 'debug')

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return user
    
    @staticmethod
    def get_current_active_user(current_user:User = Security(get_current_user))->UserInDB|None:
        if GlobalSettingService.log_lvl == logging.DEBUG:
            AuthServiceFWDI.__log__(f"{__name__}, current user:{current_user}", "debug")

        if current_user.disabled:
            AuthServiceFWDI.__log__(f"{__name__}, 400: Inactive user")
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return current_user