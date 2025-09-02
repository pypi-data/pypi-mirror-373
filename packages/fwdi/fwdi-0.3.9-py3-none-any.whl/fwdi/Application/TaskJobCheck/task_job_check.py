from ...Application.Abstractions.Core.base_task_job_check import BaseTaskJobCheck
from ..Abstractions.External.base_task_queue_manager import BaseTaskQueueManager
from ...Application.DTO.check_task_id_view_model import CheckTaskIdViewModel


class TaskJobCheck(BaseTaskJobCheck):
    
    def check_task_id(self, 
                      task_id:str,
                      name_queue:str,
                      handler: BaseTaskQueueManager)->int:
        
        result = handler.check_task_id(name_queue, task_id)
        
        return result