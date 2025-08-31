import functools
import json
from threading import Thread
from typing import TypeVar
import pika
from pika.exceptions import UnroutableError
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties, Queue
from pydantic import BaseModel

from ....Domain.Enums.types_broker_client import TypeCommandData
from ....Domain.Enums.types_broker_client import TypeBrokerClient

from ....Infrastructure.BrokerQueue.RabbitMQService.Models.command_data import CommandData
from ....Infrastructure.BrokerQueue.RabbitMQService.Models.inner_pack import InnerPackage
from ....Infrastructure.BrokerQueue.RabbitMQService.ModelEvents.broker_event import BrokerEvent
from ....Application.Abstractions.base_broker_client import BaseBrokerClient

_CLS_ = TypeVar('_CLS_', bound='RabbitMQBrokerClient')
T = TypeVar('_CLS_')

class RabbitMQBrokerClient(BaseBrokerClient):
    def __init__(self, name_queue:str, credential:dict, host:str='localhost', port:int=5672):
        self.__name_queue:str = name_queue
        self.__host:str = host
        self.__port:str = port
        self.threads = []
        self.mode:TypeBrokerClient = None
        self.__back_queue:str = f"{self.__name_queue}_back"

        self.__on_data_receive:BrokerEvent = BrokerEvent('OnDataReceive')
        """Argument (self, inner_pack:InnerPackage)"""
        
        self.__on_state_change:BrokerEvent = BrokerEvent('OnStateChange')
        """Argument (self, str, int)"""
        
        self.__on_error_processing:BrokerEvent = BrokerEvent('OnErrorProcessing')
        """Argument (self, CommandData, reply_to)"""
        
        self.__on_log:BrokerEvent = BrokerEvent('OnLog')
        """self, message:str, lvl_log:str"""
        
        self.__threads:Thread = None

        if credential['username'] and credential['password']:
            self.__credentials:pika.PlainCredentials = pika.PlainCredentials(credential['username'], credential['password'])
            self.__main_param:pika.ConnectionParameters = pika.ConnectionParameters(host=self.__host, port=self.__port, credentials=self.__credentials)
        else:
            self.__main_param:pika.ConnectionParameters = pika.ConnectionParameters(host=self.__host, port=self.__port)
            
        self.__connection_executor:pika.BlockingConnection = None
        self.__channel_executor:BlockingChannel = None
        self.__connection_consumer:pika.BlockingConnection = None
        self.__channel_consumer:BlockingChannel = None
    
    @classmethod
    def create_executor(cls:type[_CLS_],
                        name_queue:str, 
                        on_data_receive:BrokerEvent,
                        on_error_processing:BrokerEvent,
                        on_state_change:BrokerEvent,
                        on_log:BrokerEvent,
                        credential:dict,
                        host:str='localhost', 
                        port:int=5672,)->T:
        
        new_instance = cls(name_queue, credential, host, port)
        new_instance.mode = TypeBrokerClient.Executer
        new_instance.__init_executor_connection()
        new_instance.__on_data_receive += on_data_receive
        new_instance.__on_error_processing += on_error_processing
        new_instance.__on_state_change += on_state_change
        new_instance.__on_log += on_log
        new_instance.__start()

        return new_instance

    @classmethod
    def create_consumer(cls:type[_CLS_], 
                        name_queue:str, 
                        on_data_receive:BrokerEvent,
                        on_error_processing:BrokerEvent,
                        on_state_change:BrokerEvent,
                        on_log:BrokerEvent,
                        credential:dict,
                        host:str='localhost', 
                        port:int=5672,)->T:
        
        new_instance = cls(name_queue, credential, host, port)
        new_instance.mode = TypeBrokerClient.Consumer
        
        if cls.is_queue_exists(name_queue, host, port, credential):
            new_instance.__init_consumer_connection()
            new_instance.__on_data_receive += on_data_receive
            new_instance.__on_error_processing += on_error_processing
            new_instance.__on_state_change += on_state_change
            new_instance.__on_log += on_log
        
            return new_instance
        else:
            return None

    def __init_executor_connection(self):
        try:
            self.__connection_executor = pika.BlockingConnection(self.__main_param)
            self.__channel_executor = self.__connection_executor.channel()
            self.__channel_executor.confirm_delivery()
            self.__threads = Thread(target=self.__start_receive_message, daemon=False)
        except Exception as ex:
            print(f"ERROR :{ex}")

    def __init_consumer_connection(self):
        self.__connection_consumer = pika.BlockingConnection(self.__main_param)
        self.__channel_consumer = self.__connection_consumer.channel()
        self.__channel_consumer.confirm_delivery()

    def __start(self):
        if self.__connection_executor:
            self.__threads.start()

    def stop(self):
        if self.__channel_executor.is_open:
            if RabbitMQBrokerClient.is_queue_exists(self.__name_queue, self.__host, self.__port):
                active_queue=self.__name_queue if self.mode == TypeBrokerClient.Executer else self.__back_queue
                try:
                    self.__channel_executor.queue_delete(active_queue)
                except:
                    ...
       
        if self.__connection_executor.is_open:
            self.__connection_executor.close()

        if self.mode == TypeBrokerClient.Consumer:
            if self.__channel_consumer.is_open:
                self.__channel_consumer.close()
        
            if self.__connection_consumer.is_open:
                self.__connection_consumer.close()

    def __str__(self):
        return self.__class__.__name__
    
    def __del__(self):
        self.stop()

    def __callback_(self, channel:BlockingChannel, method:Basic.Deliver, properties:BasicProperties, body:bytes):
        if isinstance(body, bytes):
            request:str = body

        try:
            income_command = CommandData(**json.loads(request))
            #channel.basic_ack(method.delivery_tag)

            if income_command.count_error == 3:
                self.__on_error_processing(self, income_command, properties.reply_to)
                self.__channel_executor.basic_ack(method.delivery_tag)

            else:
                match income_command.command_id:
                    case TypeCommandData.FORWARD:
                        fn_ack = functools.partial(channel.basic_ack, method.delivery_tag)
                        inner_pack:InnerPackage = InnerPackage(package=income_command.data,
                                                            back_reply=properties.reply_to,
                                                            fn_ack=fn_ack)
                        try:
                            self.__on_data_receive(self, inner_pack)

                        except Exception as ex:
                            income_command.count_error += 1
                            self.__to_public_with_error(income_command, inner_pack.back_reply)
                    case TypeCommandData.BACK:
                        fn_ack = functools.partial(channel.basic_ack, method.delivery_tag)
                        inner_pack:InnerPackage = InnerPackage(package=income_command.data,
                                                            back_reply=properties.reply_to,
                                                            fn_ack=fn_ack)
                        
                        self.__on_data_receive(self, inner_pack)
                    case TypeCommandData.EXIT:
                        self.__on_state_change(self, 'change_state receiver', 2)
                        result = channel.queue_delete(self.__name_queue)
                        channel.basic_ack(method.delivery_tag)

                        if isinstance(result.method, Queue.DeleteOk):
                            self.__on_log(self, f"Queue: {self.__name_queue} is deleted", 'info')
                        else:
                            self.__on_log(self, f"Error: {self.__name_queue} is not deleted", 'info')

                        channel.stop_consuming()
                        channel.close()
                    case _:
                        self.__on_error_processing(self, income_command, self.__name_queue)
                        channel.basic_ack(method.delivery_tag)

        except Exception as ex:
             self.__on_log(self, f"Error: {ex}", 'error')

    def __to_public_with_error(self, model:CommandData, name_reply:str)->bool:
        if not isinstance(model, BaseModel):
            self.__on_log(self, 'Error publish only pydentic BaseModel base !', 'error')
            raise Exception('Error publish only pydentic BaseModel base !')
        
        json_str:str = model.model_dump_json()
        try:
            self.__channel_executor.basic_publish(exchange='', 
                                         routing_key=self.__name_queue, 
                                         body=json_str, 
                                         properties=pika.BasicProperties(
                                                                        reply_to=name_reply,
                                                                        content_type='application/json',
                                                                        content_encoding='utf-8'))
            return True
        except UnroutableError:
            self.__on_log(self, 'Message could not be confirmed', 'error')
            return False

    def to_reply(self, model:BaseModel, to_back_queue:str, command_id:int=2)->bool:
        
        if not isinstance(model, CommandData):
            command = CommandData(command_id=command_id, data=model.model_dump_json())
            json_command:str = command.model_dump_json()
        else:
            model.command_id = command_id
            json_command:str = model.model_dump_json()
        
        try:
            self.__channel_executor.basic_publish(exchange='', 
                                     routing_key=to_back_queue, 
                                     body=json_command,
                                     properties=pika.BasicProperties(
                                                                content_type='application/json',
                                                                delivery_mode=pika.DeliveryMode.Transient), mandatory=True)
            return True
        except UnroutableError:
            self.__on_log(self, 'Answer message could not be confirmed', 'error')
            return False

    def __start_receive_message(self):
        try:
            active_queue=self.__name_queue if self.mode == TypeBrokerClient.Executer else self.__back_queue

            self.__channel_executor.queue_declare(queue=active_queue, auto_delete=False, durable=True)
            self.__channel_executor.basic_consume(queue=active_queue, on_message_callback=self.__callback_, auto_ack=False)

            self.__on_log(self, f'[*]Start thread with receive queue: {self.__name_queue}', 'info')
            self.__on_state_change(self, 'change_state', 1)
            
            self.__channel_executor.start_consuming()
            
            self.__on_log(self, f'[*]Thread with receive queue is stoped !', 'info')
        except Exception as ex:
            self.__on_log(self, f"Error:{ex}", 'error')

    def is_queue_exists(name_queue:str, host:str, port:int, credential:dict={})->bool:
        try:
            connection_consumer:pika.BlockingConnection = None
            if credential:
                cred_param = pika.PlainCredentials(credential['username'], credential['password'])
                connection_consumer = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=cred_param))
            else:
                connection_consumer = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))

            channel_consumer:BlockingChannel = connection_consumer.channel()
            _ = channel_consumer.queue_declare(queue=name_queue,
                                        durable=True,
                                        passive=True,)
            connection_consumer.close()
            return True
        except:
            return False

    def to_publish(self, model:BaseModel)->bool:
        if not isinstance(model, BaseModel):
            self.__on_log(self, 'Error publish only pydentic BaseModel base !', 'error')
            raise Exception('Error publish only pydentic BaseModel base !')
        
        json_str:str = model.model_dump_json()
        try:
            self.__channel_consumer.basic_publish(exchange='', 
                                         routing_key=self.__name_queue, 
                                         body=json_str, 
                                         properties=pika.BasicProperties(
                                                                        reply_to=self.__back_queue,
                                                                        content_type='application/json', #'text/plain'
                                                                        content_encoding='utf-8',
                                                                        delivery_mode=pika.DeliveryMode.Transient), mandatory=True)
            return True
        except UnroutableError:
            self.__on_log(self, 'Message could not be confirmed', 'error')
            return False