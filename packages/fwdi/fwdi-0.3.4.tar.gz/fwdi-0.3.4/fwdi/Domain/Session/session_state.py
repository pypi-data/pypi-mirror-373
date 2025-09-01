from ...Domain.Session.user_session import UserSession

class SessionState():
    def __init__(self):
        self.__transcribe:dict[str:UserSession] = {}
    
    def contain(self, key:str)->bool:
        return True if key in self.__transcribe else False

    def __getitem__(self, key:str)->UserSession:
        return self.__transcribe[key]

    def __setitem__(self, key:str, user_data:UserSession):
        if not self.__transcribe.get(key, None):
            self.__transcribe[key] = user_data