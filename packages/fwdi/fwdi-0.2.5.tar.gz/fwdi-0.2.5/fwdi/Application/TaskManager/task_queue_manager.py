from ...Application.Abstractions.base_task_queue_manager import BaseTaskQueueManager
from ...Application.TaskManager.job_task import JobTask
from ...Application.TaskManager.task_queue_item import TaskQueueItem

class TaskQueueManager(BaseTaskQueueManager):
    def __init__(self) -> None:
        super().__init__()
        self.__pull_queue:dict[str, TaskQueueItem] = {}
        self.add_queue('main')

    def queue_exists(self, name:str)->bool:
        return True if name in self.__pull_queue else False

    def add_queue(self, name:str)->TaskQueueItem | None:
        TaskQueueManager.__log__(f"add_queue:{name}", 'debug')
        try:
            if not name in self.__pull_queue:
                self.__pull_queue[name] = TaskQueueItem()
                self.__pull_queue[name].start()

            return self.__pull_queue[name]        
        except Exception as ex:
            TaskQueueManager.__log__(ex, 'error')
            return None

    def check_task_id(self, pull_name:str, task_id:str)->int:
        if self.queue_exists(pull_name):
            return self.__pull_queue[pull_name].check_task(task_id)

    def add_task(self, task: JobTask, pull_name:str='main')->JobTask | None:
        TaskQueueManager.__log__(f"add_task:{task.id}, pull name:{pull_name}", 'debug')

        try:
            if self.queue_exists(pull_name):
                return self.__pull_queue[pull_name].add(task)
            else:
                TaskQueueManager.__log__(f"Error::Task pull is not exists!", 'error')
                raise Exception(f"Error::Task pull is not exists!")

        except Exception as ex:
            TaskQueueManager.__log__(ex, 'error')
            return None