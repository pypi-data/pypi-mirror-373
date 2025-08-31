import logging
from pythonjsonlogger import jsonlogger

from ...Domain.Configure.global_setting_service import GlobalSettingService

class BaseSysLogging(logging.Handler):
    def __init__(self, name:str, config:GlobalSettingService):
        self._base_name:str = name
        self._config:GlobalSettingService = config
        self._log_lvl:int = self._config.log_lvl
        self._logger:logging.Logger = None
        self._formatter = jsonlogger.JsonFormatter(
                   '%(asctime)s| %(name)s | %(levelname)s | %(thread)d | %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')
        
        super().__init__(level=self._log_lvl)
    
    def addHandler(self, handler:logging.Handler):
        if self._logger is not None:
            self._logger.addHandler(handler)
        else:
            print(f"Error logger not Init")
    
    def __call__(self, message:str, type_log:str='INFO'):
        if self._logger is None:
            raise Exception(f"Error logger is not init !")
        
        self.acquire()
        try:
            match(type_log.upper()):
                case 'INFO':
                    self._logger.info(message)
                case 'DEBUG':
                    self._logger.debug(message)
                case 'WARNING':
                    self._logger.warning(message)
                case 'ERROR':
                    self._logger.error(message)
                case _:
                    self._logger.info(message)
        
        except Exception as ex:
            print(f"GLOBAL ERROR::{ex}")
        finally:
            self.release()