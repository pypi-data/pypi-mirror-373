from .helpers import clean_display
from .vertex_point import VertexPoint
from .edge import Edge
from .curve import child_type_register as curve_type_register
from ..step_parser import StepParser

class EdgeCurve(Edge):
    type_name = 'EDGE_CURVE'

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
    start        = {clean_display(self.start)}
    end          = {clean_display(self.end)}
    geometry     = {clean_display(self.geometry)}
    same_sense   = {self.same_sense}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.start = VertexPoint(parser, args[1])
        self.end = VertexPoint(parser, args[2])
        self.geometry = curve_type_register.parse(parser, args[3])
        self.same_sense = args[4]

    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'start': self.start.get_geometry(),
            'end': self.end.get_geometry(),
            'curve': self.geometry.get_geometry(),
        }