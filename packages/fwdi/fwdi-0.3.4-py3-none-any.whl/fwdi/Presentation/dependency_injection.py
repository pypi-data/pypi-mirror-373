#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from ..Presentation.Pages.log_panel import LogPanel
from ..Presentation.Endpoints.checker_task import CheckerTask
from ..Presentation.DefaultControllers.redirect_page import RedirectHandler
from .Pages.web_service_setting_panel import WebServiceSettingPanel
from .Pages.rights_management_panel import RightsManagementPanel
from ..Application.Pages.web_main_page import WebMainPage
from ..Presentation.Web.session_manager import SessionManager
from ..Application.Abstractions.base_http_auth import BaseHttpAuth
from ..Presentation.DefaultControllers.http_auth import HttpAuthFWDI
from ..WebApp.web_application import WebApplication
from .DefaultControllers.home_controller import Controller
from .DefaultControllers.token_controller import TokenController
from .DefaultControllers.health_checks_controller import HealthChecksController


class DependencyInjection():
    from ..Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI

    def AddEndpoints(app:WebApplication)->None:
        #------------- HOME ENDPOINTS -----------------------------
        app.map_get(path="/home", endpoint=Controller().index)
        
        #-------------/HOME ENDPOINTS -----------------------------
        app.map_post(path='/token', endpoint=TokenController.post)

        #-------------/Checker task id-----------------------------
        app.map_get(f'/api/v1.0/check_task_id', CheckerTask.check_task_id)

        #-------------/WEB PAGES ENDPOINTS-------------------------
        DependencyInjection.AddWebPages(app)
    
    def AddRedirectRootPage(app:WebApplication, new_url:str):
        app.map_get(path='/', endpoint=RedirectHandler(new_url).redirect_main)
    
    def AddWebPages(app:WebApplication):
        default_config_services = WebMainPage(title='Конфигурация сервиса')
        default_config_services.add_page(WebServiceSettingPanel("Конфигурация сервиса"))
        default_config_services.add_page(RightsManagementPanel("Управление правами"))
        default_config_services.add_page(LogPanel("Лог сервиса"))
        
        app.add_web_page(default_config_services.create(), '/config', is_auth=True)

    def AddHealthChecks(app:WebApplication)->None:
        app.map_get(path="/health_checks", endpoint=HealthChecksController().index)

    def AddPresentation(services:BaseServiceCollectionFWDI)->None:
        services.AddTransient(BaseHttpAuth, HttpAuthFWDI)
        services.AddSingleton(SessionManager)
        services.AddTransient(WebServiceSettingPanel)
        services.AddTransient(RightsManagementPanel)
        services.AddTransient(LogPanel)
        services.AddLog(CheckerTask)