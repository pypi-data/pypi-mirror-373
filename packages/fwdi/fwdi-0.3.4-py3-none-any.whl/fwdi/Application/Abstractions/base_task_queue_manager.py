from abc import ABCMeta, abstractmethod
from ...Application.TaskManager.job_task import JobTask
from ...Application.TaskManager.task_queue_item import TaskQueueItem

class BaseTaskQueueManager(metaclass=ABCMeta):

    @abstractmethod
    def add_queue(self, name:str)->TaskQueueItem | None:
        ...
    
    @abstractmethod
    def add_task(self, task: JobTask, pull_name:str='main')->JobTask | None:
        ...
    
    @abstractmethod
    def queue_exists(self, name:str)->bool:
        ...

    @abstractmethod
    def check_task_id(self, pull_name:str, task_id:str)->int:
        ...