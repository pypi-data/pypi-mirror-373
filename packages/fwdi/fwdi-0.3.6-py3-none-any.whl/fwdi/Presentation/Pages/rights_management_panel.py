import gradio as gr
import pandas as pd

from fwdi.Application.Abstractions.base_gradio_request import BaseGradioRequest

from ...Domain.Session.user_session import UserSession
from ...Domain.Session.session_state import SessionState
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem

class RightsManagementPanel(BaseWebTabItem):
    def __init__(self, name):
        super().__init__(name)
        self.__user_session:UserSession = None

    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request, handler_request:BaseGradioRequest)->UserSession:
        return handler_request.get_or_create_user_session(session_state, request)

    def _get_all_users(self, user_repository:BaseUserRepositoryFWDI)->list[dict]:
        users = user_repository.get_all()

        return users

    def __load_users(self)->pd.DataFrame:
        users = self._get_all_users()
        df = pd.DataFrame(users)
        
        return gr.Dataframe(df, label='Users list:', show_row_numbers=True)

    def __save_users(self, data:gr.Dataframe)->bool:
        return f"# Users save."

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
                        # Управление правами.
                        """)

            with gr.Row():
                with gr.Column(variant='compact'):
                    data_users = gr.Dataframe(label='Users:', show_row_numbers=True)

                    with gr.Row():
                        bt_users_add = gr.Button(value='Add')
                        bt_users_del = gr.Button(value='Del')
                    bt_users_save = gr.Button(value='Save')
            
            bt_users_save.click(self.__save_users, inputs=[data_users], outputs=[md_status])

            parent_blocks.load(self.__load_tab, inputs=[user_state], outputs=[user_state])
            parent_blocks.load(self.__load_users, None, data_users)
            parent_blocks.load(self._session.get_user, None, head_footer)