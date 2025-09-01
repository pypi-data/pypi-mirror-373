from abc import abstractmethod, ABCMeta

class BaseDataStoreTools(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def read(path: str) -> list[dict]:
        ...

    @staticmethod
    @abstractmethod
    def write(lst_doc: list, path: str) -> bool:
        ...