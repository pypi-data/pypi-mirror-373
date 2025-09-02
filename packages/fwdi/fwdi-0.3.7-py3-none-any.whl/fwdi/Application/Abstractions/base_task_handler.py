from abc import ABC

from ...Application.Abstractions.base_task_callback_handler import BaseTaskCallbackHandler
from ...Application.Abstractions.base_task_queue_manager import BaseTaskQueueManager
from ...Application.TaskManager.job_task import JobTask


class BaseTaskHandler(ABC):
    def add_to_task(fn:callable, 
                    args:dict, 
                    task_manager:BaseTaskQueueManager)->JobTask|None:
        ...
    
    def add_to_task_callback(fn:callable, 
                             args:dict, 
                             param_callback:dict, 
                             task_manager:BaseTaskQueueManager,
                             callback_handler:BaseTaskCallbackHandler,
                             id:str=None,
                             )->JobTask|None:
        ...