import logging
from pythonjsonlogger import jsonlogger

from ...Application.Abstractions.base_logging import BaseSysLogging
from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Infrastructure.Logging.ElasticSearch.elastic_search_handler import ElasticsearchHandler

from elasticsearch import Elasticsearch


class ElasticSearchLogging(BaseSysLogging):
    def __init__(self, name:str, config:GlobalSettingService):
        super().__init__(name, config)
        self.es_handler:logging.Handler = None
        self.__init_log()

    def __init_log(self):
        self.formatter = jsonlogger.JsonFormatter(
                   '%(asctime)s| %(name)s | %(levelname)s | %(thread)d | %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                )

        es_host:str = self._config.elastic_log_conf.get('host', 'localhost')
        es_port:int = self._config.elastic_log_conf.get('port', 9200)
        es_user:str = self._config.elastic_log_conf.get('username', 'elastic')
        es_pass:str = self._config.elastic_log_conf.get('password', '')
        es_index:str = self._config.elastic_log_conf.get('elastic_search_index', 'microservice_system_log')

        if self.__check_avaibale_es(es_host, es_port, es_user, es_pass):
            self._logger = logging.getLogger(self._base_name)
            self._logger.setLevel(self._log_lvl)
            self.es_handler = ElasticsearchHandler(
                                            host=es_host, 
                                            port=es_port, 
                                            username=es_user, 
                                            password=es_pass, 
                                            elastic_index=es_index
                                            )
            self.es_handler.setFormatter(self.formatter)
            self._logger.addHandler(self.es_handler)
        else:
            print(f'Error Elastic not available.')

    def __check_avaibale_es(self, host:str, port:int, username:str, password:str)->bool:
        es = Elasticsearch(f'http://{host}:{port}', basic_auth=(username, password))
        
        return False if not es.ping() else True