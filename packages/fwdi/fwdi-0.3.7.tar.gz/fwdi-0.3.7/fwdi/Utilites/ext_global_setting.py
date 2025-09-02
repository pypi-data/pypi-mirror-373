import json
import os
from typing import TypeVar
from fwdi.Domain.Configure.global_setting_service import GlobalSettingService

T = TypeVar('T', bound='GlobalSettingService')

class ExtGlobalSetting():
    
    @staticmethod
    def parse_arg(**kwargs):
        config:GlobalSettingService = GlobalSettingService
        for key in kwargs:
            match key:
                case 'log_lvl':
                    config.log_lvl = kwargs.get('log_lvl', 0)
                case 'log_to_elastic':
                    config.log_to_elastic = kwargs.get('log_to_elastic', False)
                case 'elastic_log_conf':
                    config.elastic_log_conf = kwargs.get('elastic_log_conf', {})
                case 'log_to_file':
                    config.log_to_file = kwargs.get('log_to_file', False)
                case 'log_to_console':
                    config.log_to_console = kwargs.get('log_to_console', True)
                case 'file_log_conf':
                    config.file_log_conf = kwargs.get('file_log_conf', {})
                case 'log_split_by_name':
                    config.split_by_name = kwargs.get('log_split_by_name', False)
                case 'queue_name':
                    config.queue_name = kwargs.get('queue_name', '')
                case 'name':
                    config.name = kwargs.get('name', '')
                case 'description':
                    config.description = kwargs.get('description', '')
                case 'broker_conf':
                    config.broker_conf = kwargs.get('broker_conf', {})
                case 'to_zipkin':
                    config.to_zipkin = kwargs.get('to_zipkin', False)
                case 'zipkin_conf':
                    config.zipkin_conf = kwargs.get('zipkin_conf', {})
    
    @staticmethod
    def to_dict(setting:T)->dict:
        return {
            'current_host': setting.current_host,
            'current_port': setting.current_port,
            'log_lvl': setting.log_lvl,
            'log_to_elastic': setting.log_to_elastic,
            'log_to_console': setting.log_to_console,
            'log_to_file': setting.log_to_file,
            'log_split_by_name': setting.log_split_by_name,
            'file_log_conf': setting.file_log_conf,
            'elastic_log_conf': setting.elastic_log_conf,
            'queue_name': setting.queue_name,
            'name': setting.name,
            'description': setting.description,
            'broker_conf': setting.broker_conf,
            'to_zipkin': setting.to_zipkin,
            'zipkin_conf': setting.zipkin_conf
        }

    @staticmethod
    def load(filename:str)->T:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
                GlobalSettingService.current_host = data['current_host']
                GlobalSettingService.current_port = data['current_port']
                GlobalSettingService.log_lvl = data['log_lvl']
                GlobalSettingService.log_to_elastic = data['log_to_elastic']
                GlobalSettingService.log_to_console = data['log_to_console']
                GlobalSettingService.log_to_file = data['log_to_file']
                GlobalSettingService.log_split_by_name = data['log_split_by_name']
                GlobalSettingService.file_log_conf = data['file_log_conf']
                GlobalSettingService.elastic_log_conf = data['elastic_log_conf']
                GlobalSettingService.queue_name = data['queue_name']
                GlobalSettingService.name = data['name']
                GlobalSettingService.description = data['description']
                GlobalSettingService.broker_conf = data['broker_conf']
                GlobalSettingService.to_zipkin = data['to_zipkin']
                GlobalSettingService.zipkin_conf = data['zipkin_conf']
                GlobalSettingService.ssl_keyfile = data['ssl_keyfile']
                GlobalSettingService.ssl_certfile = data['ssl_certfile']
                GlobalSettingService.ssl_keyfile_password = data['ssl_keyfile_password']

    @staticmethod
    def save(model)->bool:
        try:
            json_data = json.dumps(ExtGlobalSetting.to_dict(model))
            with open("service_config.json", "w") as outfile:
                outfile.write(json_data)
            
            return True
        except Exception as ex:
            return False