import gradio as gr
import time
from uuid import uuid4

from ...Application.Abstractions.base_jwt_service_instance import BaseAuthServiceV2FWDI
from ...Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI

class SessionManager():
    def __init__(self):
        self.sessions:dict = {}
        self.current_session_id = None

    def get_current_user(self, 
                         req: gr.Request,
                         user_repository:BaseUserRepositoryFWDI,
                   auth_service:BaseAuthServiceV2FWDI):
        user = self.sessions.get(req.username)
        
        all_data = user_repository.get_all()
        user = auth_service.get_user(req.username, all_data)
        
        return user if user else None

    def get_user(self, req: gr.Request):
        session_id = req.session_hash
        timestamp = time.time()
        if req.username not in self.sessions:
            self.sessions[req.username] = [(session_id, timestamp)]
        else:
            self.sessions[req.username].append((session_id, timestamp))
            self.sessions[req.username].sort(key=lambda x: x[1]) # sort by timestamp

            if len(self.sessions[req.username]) > 5:
                self.sessions[req.username].pop(0) # remove the oldest sessions

        current_user = self.get_current_user(req)

        return f"Thanks for logging in, {req.username}, with session ID {session_id}. Current user: {current_user.username}"