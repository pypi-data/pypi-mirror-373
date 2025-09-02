from pydantic import SecretStr
from fastmcp.server.auth.providers.jwt import JWTVerifier, RSAKeyPair

class ExtRsaKeyHandler():
    def __init__(self):
        self.__key_pair:RSAKeyPair|None = None
    
    def generate(self):
        self.__key_pair = RSAKeyPair.generate()
    
    def create_token(self, 
                     subject:str, 
                     issuer:str, 
                     audience:str, 
                     scopes:list[str]):

        access_token = self.__key_pair.create_token(
                                            subject=subject,
                                            issuer=issuer,
                                            audience=audience,
                                            scopes=scopes
                                        )
        return access_token
    
    def get_public_key(self)->str:
        return self.__key_pair.public_key
    
    def get_private_key(self)->SecretStr:
        return self.__key_pair.private_key