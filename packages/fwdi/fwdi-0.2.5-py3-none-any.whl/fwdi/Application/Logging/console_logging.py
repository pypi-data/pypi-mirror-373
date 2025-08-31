import logging

from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Domain.Configure.global_setting_service import GlobalSettingService

class ConsoleLogging(BaseSysLogging):

    def __init__(self, name:str, config:GlobalSettingService):
        super().__init__(name, config)
        self.__init_log()
    
    def __init_log(self):
        self._logger:logging.Logger = logging.getLogger(self._base_name)
        self._logger.setLevel(self._log_lvl)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self._formatter)

        self._logger.addHandler(self.console_handler)