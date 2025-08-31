import gradio as gr
from fwdi.Application.Abstractions.base_gradio_request import BaseGradioRequest
from fwdi.Domain.Session.user_session import UserSession
from fwdi.Domain.Session.session_state import SessionState


class GradioRequest(BaseGradioRequest):

    def get_or_create_user_session(self, session_state:SessionState, request:gr.Request)->UserSession:
        if not session_state.contain(request.session_hash):
            session_state[request.session_hash] = UserSession(request.session_hash)
        
        return session_state[request.session_hash]