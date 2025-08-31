
from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Application.Logging.console_logging import ConsoleLogging
from ...Application.Logging.elasticsearch_logging import ElasticSearchLogging
from ...Application.Logging.file_logging import FileLogging
from ...Application.Abstractions.base_logging import BaseSysLogging

class ManagerLogging():
    new_logging:BaseSysLogging = None

    @staticmethod
    def get_logging(name:str, config:GlobalSettingService=GlobalSettingService)->BaseSysLogging:
        if not ManagerLogging.new_logging is None:
            if config.log_split_by_name:
                if ManagerLogging.new_logging._name == name:
                    return ManagerLogging.new_logging
            else:
                return ManagerLogging.new_logging
        
        return ManagerLogging.__create_new(name, config)
    
    def __create_new(name:str, config:GlobalSettingService=None):

        if config is None:
            config = GlobalSettingService

        if config.log_to_file:
            ManagerLogging.new_logging = FileLogging(name, config)

        if config.log_to_elastic:
            es_logging:BaseSysLogging = ElasticSearchLogging(name, config)
            if not es_logging.es_handler is None:
                if ManagerLogging.new_logging is not None:
                    ManagerLogging.new_logging.addHandler(es_logging.es_handler)
                else:
                    ManagerLogging.new_logging = es_logging

        if config.log_to_console:
            console_logging:BaseSysLogging = ConsoleLogging(name, config)
            if ManagerLogging.new_logging is not None:
                ManagerLogging.new_logging.addHandler(console_logging.console_handler)
            else:
                ManagerLogging.new_logging = console_logging
        
        return ManagerLogging.new_logging 