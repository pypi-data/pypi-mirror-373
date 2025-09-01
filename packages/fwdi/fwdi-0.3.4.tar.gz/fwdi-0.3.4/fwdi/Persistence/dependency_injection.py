from ..Application.Abstractions.base_manager_context import BaseManagerContextFWDI
from .manager_db_context import ManagerDbContextFWDI
from ..Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI

class DependencyInjection():
    
    @staticmethod
    def AddPersistence(services:BaseServiceCollectionFWDI)->None:
        services.AddTransient(BaseManagerContextFWDI, ManagerDbContextFWDI)