import gradio as gr
from ..Application.Abstractions.Core.base_gradio_request import BaseGradioRequest
from ..Domain.Session.user_session import UserSession
from ..Domain.Session.session_state import SessionState


class GradioRequest(BaseGradioRequest):

    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request)->UserSession:
        if not session_state.contain(request.session_hash):
            session_state[request.session_hash] = UserSession(request.session_hash)
        
        return session_state[request.session_hash]