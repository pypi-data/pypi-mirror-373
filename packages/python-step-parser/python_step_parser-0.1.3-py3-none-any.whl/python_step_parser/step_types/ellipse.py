from .helpers import clean_display
from .axis2_placement3d import Axis2Placement3d
from ..step_parser import StepParser

class Ellipse():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''ELLIPSE (
    key          = {self.key}
    name         = {self.name}
    position     = {clean_display(self.position)}
    semi_axis1   = {self.semi_axis1}
    semi_axis2   = {self.semi_axis2}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.position = Axis2Placement3d(parser, args[1])
        self.semi_axis1 = args[2]
        self.semi_axis2 = args[3]