from .helpers import clean_display
from .cartesian_point import CartesianPoint
from ..step_parser import StepParser

class VertexPoint():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''VERTEX_POINT (
    key          = {self.key}
    name         = {self.name}
    geometry     = {clean_display(self.geometry)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.geometry = CartesianPoint(parser, args[1])

    def get_geometry(self): 
        return self.geometry.get_geometry()