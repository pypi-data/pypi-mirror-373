from .helpers import clean_display
from .cartesian_point import CartesianPoint
from .topological_representation_item import TopologicalRepresentationItem
from ..step_parser import StepParser

class Vertex(TopologicalRepresentationItem):
    type_name = 'VERTEX'

    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{self.type_name} (
{self._str_args()}
)
'''

    def _str_args(self):
        return f'''{super()._str_args()}
    geometry     = {clean_display(self.geometry)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.geometry = CartesianPoint(parser, args[1])

    def get_geometry(self): 
        return self.geometry.get_geometry()