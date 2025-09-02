from .helpers import clean_display
from . import placement
from .direction import Direction
from ..step_parser import StepParser

type_name = 'AXIS2_PLACEMENT_3D'
class Axis2Placement3d(placement.Placement):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    axis         = {clean_display(self.axis)}
    direction    = {clean_display(self.direction)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.axis = Direction(parser, args[2])
        self.direction = Direction(parser, args[3])
    
    def get_geometry(self):
        return {
            'location': self.location.get_geometry(),
            'axis': self.axis.get_geometry(),
            'direction': self.direction.get_geometry(),
        }
    
placement.child_type_register.register(type_name, lambda parser, key: Axis2Placement3d(parser, key))