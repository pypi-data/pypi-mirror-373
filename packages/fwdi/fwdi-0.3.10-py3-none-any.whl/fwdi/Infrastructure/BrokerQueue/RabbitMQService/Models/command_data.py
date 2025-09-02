from uuid import uuid4
from pydantic import BaseModel

from .....Domain.Enums.types_broker_client import TypeCommandData

class CommandData(BaseModel):
    id:str = str(uuid4())
    command_id:TypeCommandData
    data:bytes | None
    count_error:int = 0
    zipkin_parent_id:int | None = None