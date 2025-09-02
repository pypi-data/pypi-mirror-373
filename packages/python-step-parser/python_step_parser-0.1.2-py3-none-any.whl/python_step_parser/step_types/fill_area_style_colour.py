from .helpers import clean_display
from .abstract_types import color_register
from ..step_parser import StepParser

class FillAreaStyleColour():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''FILL_AREA_STYLE_COLOUR (
    key          = {self.key}
    name         = {self.name}
    colour       = {clean_display(self.colour)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.colour = color_register.parse(parser, args[1])