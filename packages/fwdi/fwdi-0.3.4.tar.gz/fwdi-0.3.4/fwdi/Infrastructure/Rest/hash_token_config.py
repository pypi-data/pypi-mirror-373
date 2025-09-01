from threading import Lock
from ...Application.Abstractions.base_hash_token_config import BaseHashTokenConfig


class HashTokenConfig(BaseHashTokenConfig):
    def __init__(self):
        super().__init__()
        self.__lock:Lock = Lock()
    
    def get_token(self, base_url:str)->str|None:
        self.__lock.acquire()
        try:

            if base_url in self._hash_token:
                return self._hash_token[base_url]
            else:
                return None

        finally:
            if self.__lock.locked():
                self.__lock.release()
    
    def add_token(self, base_url:str, token:str)->bool:
        self.__lock.acquire()
        try:

            if base_url not in self._hash_token:
                self._hash_token[base_url] = token

                return True
            else:
                return False

        finally:
            if self.__lock.locked():
                self.__lock.release()        