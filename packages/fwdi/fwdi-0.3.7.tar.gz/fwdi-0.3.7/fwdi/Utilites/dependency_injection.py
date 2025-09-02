from fwdi.Application.Abstractions.base_gradio_request import BaseGradioRequest
from fwdi.Utilites.gradio_request import GradioRequest
from ..Application.Abstractions.base_jwt_tools_v2 import BaseJwtToolsV2FWDI
from ..Utilites.jwt_tools_inst import JwtToolsV2FWDI
from ..Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI

class DependencyInjection():

    @staticmethod
    def AddUtilites(services:BaseServiceCollectionFWDI)->None:
        from .jwt_tools_static import JwtToolsFWDI

        services.AddSingleton(JwtToolsFWDI)
        services.AddTransient(BaseJwtToolsV2FWDI, JwtToolsV2FWDI)
        services.AddTransient(BaseGradioRequest, GradioRequest)