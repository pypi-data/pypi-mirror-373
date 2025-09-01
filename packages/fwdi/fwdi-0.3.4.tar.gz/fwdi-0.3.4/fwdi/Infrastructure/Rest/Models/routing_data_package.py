from uuid import uuid4
from pydantic import BaseModel

class RoutingDataPackage(BaseModel):
    id:str = str(uuid4())
    host:str | None
    port:int | None
    callback_endpoint:str | None
    data:bytes