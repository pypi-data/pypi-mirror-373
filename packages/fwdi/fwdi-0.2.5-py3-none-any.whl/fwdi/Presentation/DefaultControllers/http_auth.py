from ...Application.Abstractions.base_http_auth import BaseHttpAuth
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.Abstractions.base_jwt_service_instance import BaseAuthServiceV2FWDI

class HttpAuthFWDI(BaseHttpAuth):

    def __try_auth(user:str, 
                   passw:str, 
                   user_repository:BaseUserRepositoryFWDI,
                   auth_service:BaseAuthServiceV2FWDI)->bool:
        try:
            all_data = user_repository.get_all()
            user = auth_service.authenticate_user(all_data, user, passw)

            return True if user else False
        except Exception as ex:
            HttpAuthFWDI.__log__(f"ERROR:{ex}", 'error')
            return False

    def login(username:str, 
              password:str)->tuple[bool, str]:
        """Custom authentication."""

        if HttpAuthFWDI.__try_auth(username, 
                                   password):
            HttpAuthFWDI.__log__(f"Accept Authentication {username}")
        else:
            HttpAuthFWDI.__log__(f"Wrong Authentication {username}.")
        
        return True, username        