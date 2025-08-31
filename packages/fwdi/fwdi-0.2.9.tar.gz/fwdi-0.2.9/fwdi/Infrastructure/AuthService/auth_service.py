from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError

from pydantic import ValidationError

from ...Application.Abstractions.base_jwt_service import BaseAuthServiceFWDI, oauth2_scheme
from ...Application.DTO.Auth.user_in_db import UserInDB
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.DTO.Auth.model_user import User
from ...Application.DTO.Auth.token_data import TokenData
from ...Persistence.manager_db_context import ManagerDbContextFWDI
from ...Utilites.jwt_tools import JwtToolsFWDI


class AuthServiceFWDI(BaseAuthServiceFWDI):

    @staticmethod
    def get_user(username: str, 
                    db_context:BaseUserRepositoryFWDI, 
                    jwt_tools:JwtToolsFWDI)->UserInDB|None:
        AuthServiceFWDI.__log__(f"{__name__}, db context:{db_context}, username:{username}")

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            return None
        
        AuthServiceFWDI.__log__(f"{__name__}, Authentificate:{user}")
        
        return user

    @staticmethod
    def authenticate_user(db_context:BaseUserRepositoryFWDI, 
                          username: str, 
                          password: str, 
                          jwt_tools:JwtToolsFWDI)->UserInDB|None:
        AuthServiceFWDI.__log__(f"{__name__}, db context:{db_context}, username:{username}, pass:{password}")

        user = jwt_tools.get_user_by_username(db_context, username)

        if not user:
            return None
        
        if not jwt_tools.verify_password(password, user.hashed_password):
            return None
        
        AuthServiceFWDI.__log__(f"{__name__}, Authentificate:{user}")
        
        return user
    
    @staticmethod
    def get_current_user(security_scopes: SecurityScopes, 
                         token: Annotated[str, Depends(oauth2_scheme)], 
                         jwt_tools:JwtToolsFWDI=Depends())->UserInDB|None:
        AuthServiceFWDI.__log__(f"{__name__}, SecurityScopes:{security_scopes}:{token}")
        
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
        
        AuthServiceFWDI.__log__(f"{__name__}, authenticate_value:{authenticate_value}")

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            payload = jwt_tools.decode_payload_token(token)

            AuthServiceFWDI.__log__(f"{__name__}, payload:{payload}")
            
            username: str = payload.get("sub")
            email: str = payload.get("email")
            
            if username is None:
                raise credentials_exception
            
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username, email=email)
            
            AuthServiceFWDI.__log__(f"{__name__}, token_data:{token_data}")
        except (InvalidTokenError, ValidationError) as ex:
            AuthServiceFWDI.__log__(f"Error:{ex}", 'error')
            raise credentials_exception
        
        managerdb = ManagerDbContextFWDI()
        users_db = managerdb.get_metadata_user()
        user = jwt_tools.get_user_by_email(users_db, email=token_data.email)
        
        AuthServiceFWDI.__log__(f"find user in account db:{__name__}, user:{user}")

        if user is None:
            AuthServiceFWDI.__log__(f"User not found :{users_db}", 'error')
            raise credentials_exception
        
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                AuthServiceFWDI.__log__(f"user:{user}, Not enough permissions")

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return user
    
    @staticmethod
    def get_current_active_user(current_user:User = Security(get_current_user),)->UserInDB|None:
        AuthServiceFWDI.__log__(f"{__name__}, current user:{current_user}")

        if current_user.disabled:
            AuthServiceFWDI.__log__(f"{__name__}, 400: Inactive user")
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return current_user