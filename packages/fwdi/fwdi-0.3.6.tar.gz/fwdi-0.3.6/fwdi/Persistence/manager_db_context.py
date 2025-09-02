from ..Application.DTO.Repository.model_user import *
from ..Application.Abstractions.base_manager_context import BaseManagerContextFWDI


class ManagerDbContextFWDI(BaseManagerContextFWDI):

    def get_metadata_user(self) -> User:
        ManagerDbContextFWDI.__log__(f"select {__name__}","debug")
        return User

    def get_metadata_permission(self) -> Permissions:
        ManagerDbContextFWDI.__log__(f"select {__name__}","debug")
        return Permissions

    def get_metadata_scopes(self) -> Scope:
        ManagerDbContextFWDI.__log__(f"select {__name__}","debug")
        return Scope