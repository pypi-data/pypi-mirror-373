from pydantic import BaseModel

class CheckTaskIdViewModel(BaseModel):
    name_queue:str
    task_id:str
    status:int