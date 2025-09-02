
from ..step_parser import StepParser
from .abstract_types import color_register

class ColourRGB():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''COLOUR_RGB (
    key          = {self.key}
    name         = {self.name}
    rgb          = ({self.r}, {self.g}, {self.b})
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.r = args[1]
        self.g = args[2]
        self.b = args[3]

color_register.register('COLOUR_RGB', lambda parser, key: ColourRGB(parser, key))