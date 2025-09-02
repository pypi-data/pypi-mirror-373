from abc import ABC
from fwdi.Application.Abstractions.base_task_queue_manager import BaseTaskQueueManager


class BaseTaskJobCheck(ABC):
    def check_task_id(self, 
                      task_id:str,
                      name_queue:str,
                      handler: BaseTaskQueueManager)->int:
        ...