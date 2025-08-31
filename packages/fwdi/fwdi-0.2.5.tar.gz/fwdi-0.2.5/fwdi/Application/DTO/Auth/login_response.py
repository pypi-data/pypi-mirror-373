class LoginResponse():
    def __init__(self, access_token:str, token_type:str) -> None:
        self.access_token:str = access_token
        self.token_type:str = token_type