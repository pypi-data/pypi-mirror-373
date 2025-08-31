import logging
import os
from logging.handlers import RotatingFileHandler

from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Domain.Configure.global_setting_service import GlobalSettingService


DEFAULT_BACKUP_COUNT_LOG:int = 20
MEGA_BYTE:int = 1 * 1024 * 1024
LOG_DIR:str = 'logs'


class FileLogging(BaseSysLogging):
    def __init__(self, name:str, config:GlobalSettingService):
        super().__init__(name, config)
        self.__fullpath:str = f'{LOG_DIR}/{self._base_name}.log'
        self.rotating_handler:logging.Handler = None
        self.file_handler:logging.Handler = None
        self.__init_log()
        
    def __init_log(self):
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        size_log:int = self._config.file_log_conf.get('size_log', 10)
        backupCount:int = self._config.file_log_conf.get('backupCount', 20)

        self._logger = logging.getLogger(self._base_name)
        self._logger.setLevel(self._log_lvl)

        self.rotating_handler = RotatingFileHandler(filename=self.__fullpath, 
                                                    maxBytes=size_log * MEGA_BYTE, 
                                                    backupCount=backupCount)
        self._logger.addHandler(self.rotating_handler)

        self.file_handler = logging.FileHandler(self.__fullpath)
        self.file_handler.setLevel(self._log_lvl)
              
        self.file_handler.setFormatter(self._formatter)
        self._logger.addHandler(self.file_handler)