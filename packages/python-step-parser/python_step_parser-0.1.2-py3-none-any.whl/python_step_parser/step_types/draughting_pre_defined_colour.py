
from .colour_rgb import ColourRGB
from ..step_parser import StepParser
from .abstract_types import color_register

class DraughtingPreDefinedColour():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''DRAUGHTING_PRE_DEFINED_COLOUR (
    key          = {self.key}
    name         = {self.name}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]

color_register.register('DRAUGHTING_PRE_DEFINED_COLOUR', lambda parser, key: ColourRGB(parser, key))