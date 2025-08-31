import gradio as gr
from abc import ABC, abstractmethod

from ...Presentation.Web.session_manager import SessionManager


class BaseWebPage(ABC):
    def __init__(self):
        super().__init__()
        self._session = SessionManager()
    
    @abstractmethod
    def create_panel(self)->gr.Blocks:
        ...