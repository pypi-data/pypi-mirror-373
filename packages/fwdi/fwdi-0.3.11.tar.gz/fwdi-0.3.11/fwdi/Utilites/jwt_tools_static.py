import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from ..Application.Abstractions.Core.base_user_repository import BaseUserRepositoryFWDI
from ..Application.Configs.service_config import ServiceConfig
from ..Application.DTO.Auth.user_in_db import UserInDB
from ..Application.DTO.Auth.model_user import User

class JwtToolsFWDI():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def decode_token(token:str, secret:str, algorithms:str)->dict|None:
        try:
            jwt_options = {
                            'verify_signature': False,
                            'verify_exp': False,
                            'verify_nbf': False,
                            'verify_iat': False,
                            'verify_aud': False
                        }
            encoded_jwt = jwt.decode(jwt=token, key=secret, algorithms=algorithms, options=jwt_options)
            
            return encoded_jwt
        except jwt.exceptions.DecodeError as e:
            if "Invalid crypto padding" in str(e):
                # Try adding padding

                decoded_token = jwt.decode(token + "==", algorithms=algorithms, options=jwt_options)
                if decoded_token:
                    return decoded_token
                return None
            
            return None

    @staticmethod
    def get_token(request:list[tuple[str,str]])->str|None:
        bearer_key = [tup for tup in request.headers.raw if b'authorization' in tup]
        if bearer_key:
            bearer:str = str(bearer_key[0][1])
            try:
                token:list[str] = bearer.split(' ')[1]
                return token
            except Exception as ex:
                print(f"ERROR:{ex}")
        
        return None

    @staticmethod
    def decode_payload_token(token:str, config:ServiceConfig)->any:
        JwtToolsFWDI.__log__(f"{__name__}:{token}:{config}", 'debug')

        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

        return payload

    @staticmethod
    def verify_password(plain_password:str, hashed_password:str)->bool:
        JwtToolsFWDI.__log__(f"{__name__}:{plain_password}", 'debug')

        return JwtToolsFWDI.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password:str)->str:
        JwtToolsFWDI.__log__(f"{__name__}:{password}", 'debug')

        return JwtToolsFWDI.pwd_context.hash(password)

    @staticmethod
    def get_user_by_username(db_context:BaseUserRepositoryFWDI, username: str)-> UserInDB|None:
        JwtToolsFWDI.__log__(f"{__name__}:{db_context}:{username}", 'debug')

        user = [item for item in db_context if item['username'] == username]
        if len(user) > 0:
            user_dict = user[0]
            JwtToolsFWDI.__log__(f"{user_dict}", 'debug')
            return UserInDB(**user_dict)
        else:
            return None

    @staticmethod
    def get_user_by_email(users_db:User, email: str)-> UserInDB|None:
        JwtToolsFWDI.__log__(f"{__name__}:{users_db}:{email}", 'debug')

        for user in users_db:
            if user.email == email:
                return UserInDB(**{
                        'username': user.username,
                        'hashed_password': user.hashed_password,
                        'email': user.email,
                        })

        return None

    @staticmethod
    def create_access_token(data: dict, config:ServiceConfig):
        JwtToolsFWDI.__log__(f"{__name__}:{data}:{config}", 'debug')

        to_encode = data.copy()
        expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        JwtToolsFWDI.__log__(f"{__name__}:{encoded_jwt}", 'debug')
        
        return encoded_jwt