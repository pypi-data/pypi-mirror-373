from enum import IntEnum

class TypeCommandData(IntEnum):
    FORWARD=1,
    BACK=2,
    EXIT=3,
    ERROR_PROCESSING=405,
    
class TypeBrokerClient(IntEnum):
    Consumer=0,
    Executer=1