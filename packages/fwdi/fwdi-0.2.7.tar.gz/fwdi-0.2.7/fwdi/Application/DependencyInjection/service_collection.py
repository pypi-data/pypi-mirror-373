#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from typing import overload

from ...Application.Abstractions.base_di_container import BaseDIConteinerFWDI
from ...Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI
from ...Application.Abstractions.service_descriptor import ServiceDescriptorFWDI
from ...Domain.Enums.service_life import ServiceLifetime
from .dependency_container import DependencyContainerFWDI, TService

class ServiceCollectionFWDI(BaseServiceCollectionFWDI):
    def __init__(self) -> None:        
        self._serviceDescriptor:dict[type, ServiceDescriptorFWDI] = {}

    @property
    def ServiceDescriptor(self)->set:
        return self._serviceDescriptor
#====================================================================================================================================================

    def AddLog(self, instance:type[TService]|TService):
        self._serviceDescriptor[instance] = ServiceDescriptorFWDI.create_log(instance)

#====================================================================================================================================================

    @overload
    def AddSingleton(self, instance:type[TService]|TService):
        ...

    def AddSingleton(self, base_type:type[TService]|TService=None, inst_type:type[TService]|TService=None)->TService:
        self.__add_v1(ServiceLifetime.Singleton, base_type, inst_type)

    #===========================================================================================
    @overload
    def AddTransient(self, instance:type[TService]|TService):
        ...

    def AddTransient(self, base_type:type[TService]|TService=None, inst_type:type[TService]|TService=None):
        self.__add_v1(ServiceLifetime.Transient, base_type, inst_type)

    def __add_v1(self, lifetime:ServiceLifetime, base_type:type[TService]|TService=None, inst_type:type[TService]|TService=None):
        from ...Utilites.ext_reflection import ExtReflection

        if ExtReflection.is_class(base_type):
            if base_type != None and inst_type != None:
                self._serviceDescriptor[base_type.__name__] = ServiceDescriptorFWDI.create(base_type, inst_type, lifetime)
            elif base_type != None and inst_type == None:
                self._serviceDescriptor[base_type.__name__] = ServiceDescriptorFWDI.create_from_type(base_type, lifetime)
        else:
            if lifetime == ServiceLifetime.Singleton:
                if hasattr(base_type, '__name__'):
                    self._serviceDescriptor[base_type.__name__] = ServiceDescriptorFWDI.create_from_instance(base_type, lifetime)
                else:
                    name_type:str = type(base_type).__name__
                    self._serviceDescriptor[name_type] = ServiceDescriptorFWDI.create_from_instance(base_type, lifetime)
            else:
                if not isinstance(base_type, type):
                    if hasattr(base_type, '__name__'):
                        self._serviceDescriptor[base_type.__name__] = ServiceDescriptorFWDI.create_from_instance(base_type, lifetime)
                    else:
                        name_type:str = type(base_type).__name__
                        self._serviceDescriptor[name_type] = ServiceDescriptorFWDI.create_from_instance(base_type, lifetime)

#====================================================================================================================================================

    def GenerateContainer(self)->BaseDIConteinerFWDI:
        return DependencyContainerFWDI(self._serviceDescriptor)