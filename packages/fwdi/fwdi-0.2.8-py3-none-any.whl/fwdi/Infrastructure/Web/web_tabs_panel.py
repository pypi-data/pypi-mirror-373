import gradio as gr
from gradio.themes.base import Base


from ...Application.Abstractions.base_web_tab_item import BaseWebTabItem
from ...Application.Abstractions.base_web_tabs_panel import BaseWebTabsPanel

css = """
#small span{
 font-size: 0.8em;
}
"""

class WebTabsPanel(BaseWebTabsPanel):
    def __init__(self, title:str, theme:Base=gr.themes.Glass()):
        from ...Domain.Session.session_state import SessionState
        self.__theme:Base = theme
        self.__main_blocks:gr.Blocks = gr.Blocks(css=css, theme=self.__theme, title=title)
        self.__tabs:gr.Tabs = None
        self.__actual_tabs:dict[str, int] = {}
        self.__session_state:SessionState = SessionState()
        self.web_state:gr.State = None
    
    def create_panel(self, lst_comp:list[BaseWebTabItem])->gr.Blocks:
        with self.__main_blocks:
            self.web_state = gr.State(self.__session_state)
            if not self.__tabs:
                self.__tabs = gr.Tabs()

            with self.__tabs:
                for index, item in enumerate(lst_comp):
                    item.create_tab(self.__main_blocks, self.__tabs, self.web_state, index)
                    self.__actual_tabs[item.Name] = index

        return self.__main_blocks