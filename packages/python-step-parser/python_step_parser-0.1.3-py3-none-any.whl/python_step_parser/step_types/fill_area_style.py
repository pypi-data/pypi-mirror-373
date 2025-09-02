from .helpers import clean_display_list
from .fill_area_style_colour import FillAreaStyleColour
from ..step_parser import StepParser

class FillAreaStyle():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''FILL_AREA_STYLE (
    key          = {self.key}
    name         = {self.name}
    fill_styles  = {clean_display_list(self.fill_styles)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.fill_styles = [FillAreaStyleColour(parser, arg) for arg in args[1]]