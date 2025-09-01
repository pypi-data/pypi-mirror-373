from pydantic import BaseModel
from ..Abstractions.base_task_callback_handler import BaseTaskCallbackHandler
from ..Abstractions.base_rest_client import BaseRestClientFWDI
from ...Infrastructure.Configs.rest_client_config import RestClientConfig

class TaskCallbackHandler(BaseTaskCallbackHandler):
    def __init__(self):
        super().__init__()

    def callback_result(self, 
                        param_callback:dict, 
                        model:BaseModel, 
                        rest_client:BaseRestClientFWDI):
        
        config = RestClientConfig()
        config.port = param_callback.get('port')
        config.server = param_callback.get('host')
        config.username = param_callback.get('username')
        config.password = param_callback.get('pass')
        callback_route_api:str = param_callback.get('endpoint')
        
        rest_client.init(config=config)

        try:
            if not rest_client.IsAuth:
                if not rest_client.login():
                    TaskCallbackHandler.__log__(f"Error auth", 'error')
                    raise Exception(f'Error auth to {config.server}:{config.port}/{callback_route_api}')

            if not model == None:
                result, code = rest_client.post(path=callback_route_api, model=model)

                if code != 200:
                    print(f"Error send (TaskHandler->__callback_result) data to callback rest service.")
            else:
                TaskCallbackHandler.__log__(f"error model=None", 'error')
                return None
            
        except Exception as ex:
            TaskCallbackHandler.__log__(f"Error: {ex}", 'error')
            return None