#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from .routeble import RoutebleFWDI
from ...Utilites.ext_controller import ExtController

class BaseControllerFWDI(RoutebleFWDI):
    def __init__(self, base_path:str='/'):
        super().__init__()
        self.base_path:str = base_path
        self.__create_endpoint(type(self))

    def get_base_path(self)->str:
        return self.base_path
    
    def __create_endpoint(self, type_inst:type):
        from ...Utilites.ext_reflection import ExtReflection

        path_name = ExtController.get_controller_name(type_inst.__name__)
        lst_method = ExtReflection.list_class_methods(type_inst, False)
        for item in lst_method:
            name, handler_method = item
            handler_method = getattr(self, name)           
            path = f"{self.base_path}{path_name}"
            self.add_api_route(path=path, endpoint=handler_method, methods=[name.upper()]) # use decorator