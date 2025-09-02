import logging

class GlobalSettingService():
    current_host:str
    current_port:int
    log_lvl:int = logging.INFO
    log_to_elastic:bool = False
    log_to_console:bool = False
    log_to_file:bool = False
    log_split_by_name:bool = False
    file_log_conf:dict = {
        'size_log':10,
        'backupCount': 20
    }
    elastic_log_conf:dict = {
                            'host': 'localhost', 
                            'port': 9200, 
                            'elastic_search_index': 'system_log', 
                            'username': 'elastic', 
                            'password': ''
                         },
    queue_name:str = ''
    name:str = ''
    description:str = ''
    use_broker:bool = False
    broker_conf:dict = {
                        'type': 'rabbitmq',
                        'host': 'localhost', 
                        'port': 5672 
                        },
    to_zipkin:bool = False
    zipkin_conf:dict = {
                        'key': 'value'
                        }
    ssl_keyfile:str = ""
    ssl_certfile:str = ""
    ssl_keyfile_password:str = ""