import gradio as gr
import pandas as pd

from fwdi.Application.Abstractions.base_gradio_request import BaseGradioRequest

from ...Utilites.ext_file import ExtFile
from ...Domain.Session.user_session import UserSession
from ...Domain.Session.session_state import SessionState
from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem



class LogPanel(BaseWebTabItem):
    def __init__(self, name):
        super().__init__(name)
        self.__user_session:UserSession = None

    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request, handler_request:BaseGradioRequest)->UserSession:
        return handler_request.get_or_create_user_session(session_state, request)

    def __load_log_files(self)->pd.DataFrame:
        lst_file_log:list = ExtFile.get_folder_files('logs')
        df = pd.DataFrame(lst_file_log)
        
        return gr.Dataframe(df, label='Logs file:', show_row_numbers=True, show_copy_button=True, interactive=False, type="array")

    def __select_log_file(self, df: pd.DataFrame,  evt: gr.SelectData):
        selected_row = df[evt.index[0]]
        file_path:str = f"{selected_row[0]}/{selected_row[1]}"
        file_context:str = ''
        count_line:int = 0
        with open(file_path, mode="r+", encoding="utf-8") as f:
            for line in f:
                file_context += f"###### {count_line} - {line}"
                count_line += 1

        return file_context

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
                        # Просмотр логов.
                        """)

            with gr.Row():
                with gr.Column(variant='compact'):
                    files_log = gr.Dataframe(label='Logs file:', show_row_numbers=True, interactive=False, type="array")

            with gr.Row():
                #log_viewer = gr.Textbox(lines=45, label="Log", placeholder="Text  log")
                log_viewer = gr.Markdown(label="Log file", line_breaks=True)

            parent_blocks.load(self.__load_tab, inputs=[user_state], outputs=[user_state])
            parent_blocks.load(self.__load_log_files, None, files_log)
            parent_blocks.load(self._session.get_user, None, head_footer)

            files_log.select(self.__select_log_file, inputs=[files_log], outputs=[log_viewer])