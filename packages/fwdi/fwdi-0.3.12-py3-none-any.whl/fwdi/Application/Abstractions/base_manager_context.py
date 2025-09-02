from ...Application.DTO.Repository.model_user import User, Permissions, Scope
from abc import ABC, abstractmethod


class BaseManagerContextFWDI(ABC):
     
     @abstractmethod
     def get_metadata_user(self) -> User:
          pass

     @abstractmethod
     def get_metadata_permission(self) -> Permissions:
          pass

     @abstractmethod
     def get_metadata_scopes(self) -> Scope:
          pass