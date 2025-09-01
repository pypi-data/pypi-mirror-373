from abc import ABC, abstractmethod

from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem

class BaseWebMainPage(ABC):
    def __init__(self):
        super().__init__()
        from ...Domain.Session.session_state import SessionState
        self.session_state:SessionState = SessionState()


    @abstractmethod
    def add_page(self, item:BaseWebTabItem):
        ...
    
    @abstractmethod
    def create(self):
        ...