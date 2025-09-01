import gradio as gr
from gradio.themes.base import Base
from ...Application.Abstractions.base_web_main_page import BaseWebMainPage
from ...Application.Abstractions.base_web_tabs_panel import BaseWebTabsPanel

from ...Infrastructure.Web.web_tabs_panel import WebTabsPanel
from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem

class WebMainPage(BaseWebMainPage):
    def __init__(self, title:str, theme:Base=gr.themes.Glass()):
        super().__init__()
        self.__panel:BaseWebTabsPanel = WebTabsPanel(title, theme)
        self.__lst_page:list[BaseWebTabItem] = []

    def add_page(self, item:BaseWebTabItem):
        self.__lst_page.append(item)

    def create(self):
        main_blocks = self.__panel.create_panel(self.__lst_page)
        return main_blocks