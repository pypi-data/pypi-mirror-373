#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import logging
from time import perf_counter_ns
from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Application.Abstractions.base_di_container import BaseDIConteinerFWDI, TService
from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Application.Logging.manager_logging import ManagerLogging


class ResolveProviderFWDI():
    __container:BaseDIConteinerFWDI = None
    __log__:BaseSysLogging = None

    def __init__(self, container:BaseDIConteinerFWDI) -> None:
        if not ResolveProviderFWDI.__log__:
            ResolveProviderFWDI.__log__ = ManagerLogging.get_logging('ResolveProviderFWDI')

        if not ResolveProviderFWDI.__container:
            ResolveProviderFWDI.__container = container

    @staticmethod
    def is_init()->bool:
        return False if not ResolveProviderFWDI.__container else True

    @staticmethod
    def get_service(cls:TService)->TService | None:

        if not ResolveProviderFWDI.__container:
            raise Exception('Not initialize ResolveProvider !')

        if GlobalSettingService.log_lvl == logging.DEBUG:
            ResolveProviderFWDI.__log__(f"{__name__}, cls:{cls}")

        return ResolveProviderFWDI.__container.GetService(cls)

    @staticmethod
    def contains(cls:TService)->bool:
        if not ResolveProviderFWDI.__container:
            raise Exception('Not initialize ResolveProvider !')

        if GlobalSettingService.log_lvl == logging.DEBUG:
            ResolveProviderFWDI.__log__(f"{__name__}, cls:{cls}")

        return ResolveProviderFWDI.__container.contains(cls)