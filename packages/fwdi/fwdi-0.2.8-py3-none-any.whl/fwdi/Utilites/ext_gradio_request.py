import gradio as gr
from fwdi.Domain.Session.user_session import UserSession
from fwdi.Domain.Session.session_state import SessionState


class ExtGradioRequest():
    @staticmethod
    def get_or_create_user_session(session_state:SessionState, request:gr.Request):
        if not session_state.contain(request.session_hash):
            session_state[request.session_hash] = UserSession(request.session_hash)
        
        return session_state[request.session_hash]