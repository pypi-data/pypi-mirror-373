from .helpers import clean_display
from .cartesian_point import CartesianPoint
from .vector import Vector
from . import curve
from ..step_parser import StepParser

class Line(curve.Curve):
    type_name = 'LINE'

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
    point        = {clean_display(self.point)}
    direction    = {clean_display(self.direction)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.point = CartesianPoint(parser, args[1])
        self.direction = Vector(parser, args[2])
        
    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'point': self.point.get_geometry(),
            'dir': self.direction.get_geometry(),
        }

curve.child_type_register.register('LINE', lambda parser, key: Line(parser, key))