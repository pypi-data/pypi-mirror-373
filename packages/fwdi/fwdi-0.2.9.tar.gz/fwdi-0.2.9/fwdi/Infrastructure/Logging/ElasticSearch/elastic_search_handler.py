import logging
from elasticsearch import Elasticsearch
import datetime
from datetime import datetime, timezone
import psutil
import socket

class ElasticsearchHandler(logging.Handler):

    def __init__(self, host:str, port:int, username:str, password:str, elastic_index:str, level = 0):
        super().__init__(level)
        self.__elastic_index:str = elastic_index
        self.__es = Elasticsearch(f'http://{host}:{port}', basic_auth=(username, password))

    def emit(self, record):
        try:
            log_entry = self.format(record)
            
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "host": socket.gethostname(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger_name": record.name,
                "process_id": record.process,
                "thread_id": record.thread,
                "system_info": self._get_system_info()
            }
            
            if isinstance(log_entry, dict):
                log_data.update(log_entry)
            
            self.__es.index(index=self.__elastic_index, body=log_data)
        except Exception as e:
            print(f"Failed to send log to Elasticsearch: {e}")
    
    def _get_system_info(self):
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }