from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ..Abstractions.base_manager_context import BaseManagerContextFWDI

class UserRepositoryFWDI(BaseUserRepositoryFWDI):
    
    def get_all(self, manager_db_context: BaseManagerContextFWDI)->list[dict]:
        UserRepositoryFWDI.__log__(f"{__name__}:{manager_db_context}", 'debug')
        
        users = manager_db_context.get_metadata_user()
        user_list = []
        for user in users:
            dct_user = {
                        'username': user.username,
                        'hashed_password': user.hashed_password,
                        'email': user.email
                        }
            user_list.append(dct_user)
        UserRepositoryFWDI.__log__(f"{user_list}", 'debug')

        return user_list

    def get_user_scopes(self, email:str, manager_db_context: BaseManagerContextFWDI)->list[str]|None:
        UserRepositoryFWDI.__log__(f"{__name__}:{manager_db_context}:{email}", 'debug')
        
        user = manager_db_context.get_metadata_user().get(manager_db_context.get_metadata_user().email == email)
        UserRepositoryFWDI.__log__(f"{user}", 'debug')

        if user != None:
            scopes_user = user.scopes.scopes_detail
            scopes = []
            for scope in scopes_user:
                scopes.append(scope.name)
            UserRepositoryFWDI.__log__(f"{scopes_user}", 'debug')

            return scopes
        else:
            UserRepositoryFWDI.__log__(f"Error user not found!", 'error')
            return None