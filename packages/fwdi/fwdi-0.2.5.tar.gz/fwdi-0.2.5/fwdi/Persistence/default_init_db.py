from ..Application.DTO.Repository.model_user import *
from ..Application.Abstractions.db_context import db

class DefaultInitializeDB():
    
    @staticmethod
    def init_db(scopes:dict[str,str]):
        db.connect()
        db.create_tables([Scope, Permissions, User, Permissions.scopes_detail.get_through_model()], safe = True)
        DefaultInitializeDB.__default_data(scopes)
        db.close()

    @staticmethod
    def __default_data(scopes:dict[str,str]):
        if len(Scope.select()) == 0:
            for scope in scopes:
                tmp_scope = Scope(name=scope, description=scopes[scope])
                tmp_scope.save()
            
        
        if len(Permissions.select()) == 0:
            default_user_permission = Permissions(name='Admin')
            default_user_permission.save()

            for scope in Scope().select():
                default_user_permission.scopes_detail.add(scope)

            default_user_permission.save()
        
        from ..Utilites.jwt_tools_inst import JwtToolsV2FWDI
        if len(User.select()) == 0:
            user = User(username='admin', 
                        full_name='Administrator', 
                        email='admin@admin.ru', 
                        hashed_password=JwtToolsV2FWDI().get_password_hash('admin'), 
                        disabled=False, scopes=default_user_permission)
            user.full_name = "Admin adminich"
            user.save()