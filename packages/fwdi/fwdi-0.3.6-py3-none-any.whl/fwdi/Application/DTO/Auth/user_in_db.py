from .model_user import User

class UserInDB(User):
    username:str
    hashed_password: str
    email:str