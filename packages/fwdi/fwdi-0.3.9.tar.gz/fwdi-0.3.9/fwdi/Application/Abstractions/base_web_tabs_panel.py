from abc import ABC, abstractmethod
import gradio as gr

from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem

class BaseWebTabsPanel(ABC):
    
    @abstractmethod
    def create_panel(self, lst_comp:list[BaseWebTabItem])->gr.Blocks:
        ...