from ...Application.Abstractions.base_task_callback_handler import BaseTaskCallbackHandler
from ...Application.Abstractions.base_task_handler import BaseTaskHandler
from ...Application.Abstractions.base_task_queue_manager import BaseTaskQueueManager
from ...Application.TaskManager.job_task import JobTask


class TaskHandler(BaseTaskHandler):
    
    @staticmethod
    def add_to_task(fn:callable, 
                    args:dict, 
                    task_manager:BaseTaskQueueManager)->JobTask|None:
        
        job:JobTask = JobTask(fn=fn, args=args, fn_callback=None, param_callback=None)
       
        TaskHandler.__log__(f"Start new job task: {job.id}", 'debug')

        return task_manager.add_task(job)

    @staticmethod
    def add_to_task_callback(fn:callable, 
                             args:dict, 
                             param_callback:dict, 
                             task_manager:BaseTaskQueueManager,
                             callback_handler:BaseTaskCallbackHandler,
                             id:str=None,
                             )->JobTask|None:
        
        job:JobTask = JobTask(fn=fn, 
                              args=args,
                              id=id,
                              fn_callback=callback_handler.callback_result,
                              param_callback=param_callback)
       
        TaskHandler.__log__(f"Start new job task: {job.id}", 'debug')

        return task_manager.add_task(job)