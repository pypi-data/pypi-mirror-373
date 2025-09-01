from abc import ABCMeta, abstractmethod

from pydantic import BaseModel
from fwdi.Application.Abstractions.base_rest_client import BaseRestClientFWDI


class BaseTaskCallbackHandler(metaclass=ABCMeta):

    @abstractmethod
    def callback_result(self, 
                        model:BaseModel, 
                        param_callback:dict, 
                        rest_client:BaseRestClientFWDI):
        ...