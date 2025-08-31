import logging
import requests
from pydantic import BaseModel

from ...Domain.Configure.global_setting_service import GlobalSettingService

from ...Application.Abstractions.base_hash_token_config import BaseHashTokenConfig
from ...Application.Abstractions.base_rest_client import BaseRestClientFWDI
from ...Application.DTO.Auth.login_response import LoginResponse

from ...Infrastructure.Configs.rest_client_config import RestClientConfig


class RestClientFWDI(BaseRestClientFWDI):
    def __init__(self, hash_config:BaseHashTokenConfig|None=None):
        super().__init__()
        self.__config:RestClientConfig = None
        self.__hash_config:BaseHashTokenConfig = hash_config
        self.__is_init:bool = False
        self.__base_url:str = ''
        self.__is_auth: bool = False
        self.__token:str = ''

    def init(self, config:RestClientConfig):
        if hasattr(RestClientFWDI, '__log__'):
            RestClientFWDI.__log__(f"{__name__}:{config}", 'debug')
        else:
            print(f"{__name__}:{config}", 'debug')
        
        self.__config = config
        if hasattr(config, 'security_layer'):
            self.__schem:str = 'http' if not config.security_layer else 'https'
        else:
            self.__schem:str = 'http'

        self.__base_url = f'{self.__schem}://{self.__config.server}:{self.__config.port}'
        self.__headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization':''
        }
        self.__is_init = True
    
    @property
    def IsAuth(self):
        if self.__hash_config:
            if token:=self.__hash_config.get_token(self.__base_url):
                self.__token = token
                self.__is_auth = True
                self.__headers["Authorization"] = f"Bearer {self.__token}"
                return True

        return self.__is_auth if self.__is_init else False
        

    def login(self, url:str='/token')->bool:
        if not self.__is_init:
            raise Exception("RestClient not init !!!")
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{url}", 'debug')
            else:
                print(f"{__name__}:{url}", 'debug')

        with requests.post(f'{self.__base_url}{url}', 
                                 data = {'username': self.__config.username,'password': self.__config.password}) as rest_req:
            response = rest_req
        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{response}", 'debug')
            else:
                print(f"{__name__}:{response}", 'debug')

        if response.status_code == 200:
            response_json = response.json()
            if 'access_token' in response_json:
                response_toke = LoginResponse(**response.json())
                self.__token = response_toke.access_token
                self.__headers["Authorization"] = f"Bearer {self.__token}"
                self.__is_auth = True
                if self.__hash_config:
                    self.__hash_config.add_token(self.__base_url, response_toke.access_token)
                
                response.close()
                if hasattr(RestClientFWDI, '__log__'):
                    RestClientFWDI.__log__(f"{__name__}:Auth is ok.", 'debug')
                else:
                    print(f"{__name__}:Auth is ok.", 'debug')

                return True
            else:
                print(f'RestClientFWDI::Error auth:{response}')
                unknow_error = response.json()
                print(unknow_error)
                if hasattr(RestClientFWDI, '__log__'):
                    RestClientFWDI.__log__(f"{__name__}:RestClientFWDI::{unknow_error}", 'debug')
                else:
                    print(f"{__name__}:RestClientFWDI::{unknow_error}", 'debug')

                response.close()
                return False
        elif response.status_code == 401:
            error_auth = response.json()
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"RestClientFWDI::Error:{error_auth}, code: {response.status_code}", 'debug')
            else:
                print(f"RestClientFWDI::Error:{error_auth}, code: {response.status_code}", 'debug')
            
            response.close()
            return False
    
    def get(self, path:str, model:BaseModel=None)->tuple | None:
        if not self.__is_init:
            raise Exception("RestClient not init !!!")

        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{path}:{model}", 'debug')
            else:
                print(f"{__name__}:{path}:{model}", 'debug')

        if model is not None:
            with requests.get(f"{self.__base_url}{path}", data=model.model_dump_json(), headers=self.__headers) as rest:
                response_get = rest
        else:
            with requests.get(f"{self.__base_url}{path}", headers=self.__headers) as rest:
                response_get = rest
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{response_get}", 'debug')
            else:
                print(f"{__name__}:{response_get}", 'debug')

        if response_get.status_code == 200:
            result = (response_get.json(), response_get.status_code)
            response_get.close()
            
            del response_get

            return result
        else:
            error_json = response_get.json()
            if 'detail' in error_json:
                if error_json['detail'] == 'Could not validate credentials':
                    if self.login():
                        return self.get(path, model)
                    
            result = (response_get, response_get.status_code)
            response_get.close()

            del response_get

            return result

    def post(self, path:str, model:BaseModel)->tuple | None:
        if not self.__is_init:
            raise Exception("RestClient not init !!!")

        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{path}:{model}", 'debug')
            else:
                print(f"{__name__}:{path}:{model}", 'debug')

        with requests.post(f"{self.__base_url}{path}", data=model.model_dump_json(), headers=self.__headers) as rest:
            response_post = rest
        
        if GlobalSettingService.log_lvl == logging.DEBUG:
            if hasattr(RestClientFWDI, '__log__'):
                RestClientFWDI.__log__(f"{__name__}:{response_post}", 'debug')
            else:
                print(f"{__name__}:{response_post}", 'debug')

        if response_post.status_code == 200:
            result = response_post.json(), response_post.status_code
            response_post.close()
            
            del response_post

            return result
        else:
            error_json = response_post.json()
            if 'detail' in error_json:
                if error_json['detail'] == 'Could not validate credentials':
                    if self.login():
                        return self.post(path, model)

            result = (response_post, response_post.status_code)
            response_post.close()
            
            del response_post

            return result