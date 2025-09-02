from fastapi import Depends

from ...Utilites.ext_rest_response import ExtRestResponse
from ...Application.TaskJobCheck.task_job_check import TaskJobCheck
from ...Application.DTO.check_task_id_view_model import CheckTaskIdViewModel


class CheckerTask():
    
    @staticmethod
    def check_task_id(model:CheckTaskIdViewModel,
                      handler:TaskJobCheck=Depends()):
        
        result = handler.check_task_id(model.task_id, model.name_queue)
        model.status = result
        
        return ExtRestResponse.make_response_200(model)
