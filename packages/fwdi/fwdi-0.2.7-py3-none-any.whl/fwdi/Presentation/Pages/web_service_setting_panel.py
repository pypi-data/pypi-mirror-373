import logging
import gradio as gr
import pandas as pd

from fwdi.Application.Abstractions.base_gradio_request import BaseGradioRequest
from fwdi.Utilites.gradio_request import GradioRequest

from ...Domain.Session.user_session import UserSession
from ...Domain.Session.session_state import SessionState
from ...Domain.Configure.global_setting_service import GlobalSettingService
from ...Utilites.ext_dictionary import ExtDictionary
from ...Utilites.ext_global_setting import ExtGlobalSetting

from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem

class WebServiceSettingPanel(BaseWebTabItem):
    def __init__(self, name):
        super().__init__(name)
        self.__lvl_log:list[str] = ["INFO",
                                    "DEBUG",
                                    "ERROR",
                                    "WARNING",
                                    "CRITICAL"]
        self.__user_session:UserSession = None
   
    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request, handler_request:BaseGradioRequest)->UserSession:
        return handler_request.get_or_create_user_session(session_state, request)

    def __save(self, 
               tb_name:str,
               tb_description:str,
               dd_log_lvl:str,
               cb_log_to_elastic:bool,
               cb_log_split_by_name:bool,
               data_elastic_log_conf:pd.DataFrame,
               cb_log_to_console:bool,
               cb_log_to_file:bool,
               tb_queue_name:str,
               data_broker_conf:pd.DataFrame,
               cb_to_zipkin:bool,
               data_zipkin_conf:pd.DataFrame):
        
        GlobalSettingService.name = tb_name
        GlobalSettingService.description = tb_description
        GlobalSettingService.log_lvl = logging._nameToLevel[dd_log_lvl]
        GlobalSettingService.log_to_elastic = cb_log_to_elastic
        GlobalSettingService.log_split_by_name = cb_log_split_by_name
        GlobalSettingService.elastic_log_conf = data_elastic_log_conf.to_dict('records')[0]
        GlobalSettingService.log_to_console = cb_log_to_console
        GlobalSettingService.log_to_file = cb_log_to_file
        GlobalSettingService.queue_name = tb_queue_name
        GlobalSettingService.broker_conf = data_broker_conf.to_dict('records')[0]
        GlobalSettingService.to_zipkin = cb_to_zipkin
        GlobalSettingService.zipkin_conf = data_zipkin_conf.to_dict('records')[0]

        if ExtGlobalSetting.save(GlobalSettingService):
            return f"Save setting to file."
        else:
            return f"Error saving setting file."

    def __load(self):
        tb_name = GlobalSettingService.name
        tb_description = GlobalSettingService.description
        dd_log_lvl = logging._levelToName[GlobalSettingService.log_lvl]
        cb_log_to_elastic = GlobalSettingService.log_to_elastic
        cb_log_split_by_name = GlobalSettingService.log_split_by_name
        data_elastic_log_conf = gr.Dataframe(ExtDictionary.to_pandas(GlobalSettingService.elastic_log_conf), label='Elastic config:', show_row_numbers=True)
        cb_log_to_console = GlobalSettingService.log_to_console
        cb_log_to_file = GlobalSettingService.log_to_file
        tb_queue_name = GlobalSettingService.queue_name
        data_broker_conf = gr.Dataframe(ExtDictionary.to_pandas(GlobalSettingService.broker_conf), label='Broker config:', show_row_numbers=True)
        cb_to_zipkin = GlobalSettingService.to_zipkin
        data_zipkin_conf = gr.Dataframe(ExtDictionary.to_pandas(GlobalSettingService.zipkin_conf), label='Zipkin config:', show_row_numbers=True)

        return tb_name, tb_description, dd_log_lvl, cb_log_to_elastic, \
                cb_log_split_by_name, cb_log_to_console, cb_log_to_file,\
                tb_queue_name, cb_to_zipkin, data_elastic_log_conf, \
                      data_broker_conf, data_zipkin_conf

    def __load_tab(self, session_state:SessionState, request:gr.Request):
        if not self.__user_session:
            self.__user_session = self.get_or_create_user_session(session_state, request)
        
        return session_state

    def create_tab(self, parent_blocks:gr.Blocks, parent:gr.Tabs, user_state:gr.State, tab_id:int):

        with gr.Tab(label=self.Name, id=tab_id) as tab:
            with gr.Row():
                head_footer = gr.Markdown(value="User not logged in")
                md_status = gr.Markdown(value="...")

            with gr.Row():
                gr.Markdown("""
                        # Страница конфигурации сервиса.
                        """)

            with gr.Row():
                with gr.Column():
                    tb_name = gr.Textbox(label='Name service:')
                    tb_description = gr.Textbox(label='Description service:')
                    dd_log_lvl = gr.Dropdown(choices=self.__lvl_log, label='Login level:')
                    cb_log_to_elastic = gr.Checkbox(label='Enable elastic:')
                    cb_log_split_by_name = gr.Checkbox(label='Login file split by name:')
                    data_elastic_log_conf = gr.Dataframe(label='Elastic login config:')
                    cb_log_to_console = gr.Checkbox(label='Login to console:')
                    cb_log_to_file = gr.Checkbox(label='Login to file:')
                    tb_queue_name = gr.Textbox(label='Queue name:')
                    data_broker_conf = gr.Dataframe(label='Broker config:')
                    cb_to_zipkin = gr.Checkbox(label='Enable zipkin service:')
                    data_zipkin_conf = gr.Dataframe(label='Zipkin config:')

                    bt_save = gr.Button(value='Save')

                
            bt_save.click(self.__save, inputs=[tb_name, 
                                            tb_description, 
                                            dd_log_lvl, 
                                            cb_log_to_elastic,
                                            cb_log_split_by_name,
                                            data_elastic_log_conf,
                                            cb_log_to_console,
                                            cb_log_to_file,
                                            tb_queue_name,
                                            data_broker_conf,
                                            cb_to_zipkin,
                                            data_zipkin_conf], outputs=[md_status])

            parent_blocks.load(self.__load_tab, inputs=user_state, outputs=user_state)
            parent_blocks.load(self._session.get_user, None, head_footer)
            parent_blocks.load(self.__load, inputs=None,
                                                outputs=[tb_name, 
                                                    tb_description, 
                                                    dd_log_lvl, 
                                                    cb_log_to_elastic,
                                                    cb_log_split_by_name,
                                                    cb_log_to_console,
                                                    cb_log_to_file,
                                                    tb_queue_name,
                                                    cb_to_zipkin,
                                                    data_elastic_log_conf,
                                                    data_broker_conf,
                                                    data_zipkin_conf])