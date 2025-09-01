from abc import ABC, abstractmethod

from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ..Configs.service_config import ServiceConfig
from ...Application.DTO.Auth.model_user import User
from ...Application.DTO.Auth.user_in_db import UserInDB


class BaseJwtToolsV2FWDI(ABC):

    @abstractmethod
    def decode_payload_token(self, token:str, config:ServiceConfig)->any:
        ...
    
    @abstractmethod
    def verify_password(self, plain_password:str, hashed_password:str)->bool:
        ...

    @abstractmethod
    def get_password_hash(self, password:str)->str:
        ...
    
    @abstractmethod
    def get_user_by_username(self, db_context:BaseUserRepositoryFWDI, username: str)-> UserInDB|None:
        ...
    
    @abstractmethod
    def get_user_by_email(self, users_db:User, email: str)-> UserInDB|None:
        ...
    
    @abstractmethod
    def create_access_token(self, data: dict, config:ServiceConfig):
        ...
