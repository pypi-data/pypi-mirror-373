#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from abc import ABCMeta, abstractmethod
from typing import TypeVar, overload

from .base_di_container import BaseDIConteinerFWDI

TService = TypeVar('TService')

class BaseServiceCollectionFWDI(metaclass=ABCMeta):

    @abstractmethod
    def AddLog(self, inst:TService):
        ...

    @overload
    @abstractmethod
    def AddSingleton(self, inst:TService):
        ...

    @overload
    @abstractmethod
    def AddSingleton(self, inst_type:type[TService]):
        ...
    
    @overload
    @abstractmethod    
    def AddSingleton(self, base_type:type[TService]=None, inst_type:type[TService]=None)->TService:
        ...
        
    @overload
    def AddTransient(self, instance:TService):
        ...

    @overload
    @abstractmethod
    def AddTransient(self, base_type:type[TService]):
        ...

    @overload
    @abstractmethod
    def AddTransient(self, base_type:type[TService]=None, inst_type:type[TService]=None):
        ...
    
    @abstractmethod
    def GenerateContainer(self)->BaseDIConteinerFWDI:
        ...
