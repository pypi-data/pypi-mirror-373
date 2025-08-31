from abc import abstractmethod
import gradio as gr

from fwdi.Domain.Session.session_state import SessionState
from fwdi.Domain.Session.user_session import UserSession


class BaseGradioRequest():
    
    @abstractmethod
    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request)->UserSession:
        ...