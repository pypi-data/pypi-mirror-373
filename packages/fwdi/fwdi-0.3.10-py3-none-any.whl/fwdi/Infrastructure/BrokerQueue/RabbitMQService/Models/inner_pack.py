import dataclasses
from uuid import uuid4

from .....Infrastructure.BrokerQueue.RabbitMQService.Models.command_data import CommandData

@dataclasses.dataclass
class InnerPackage:
    id:str = str(uuid4())
    package: bytes | None = None
    back_reply:str = ''
    fn_ack: callable = None