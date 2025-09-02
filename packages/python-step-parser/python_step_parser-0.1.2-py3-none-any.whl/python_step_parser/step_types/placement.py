from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from .cartesian_point import CartesianPoint
from . import geometric_representation_item
from ..step_parser import StepParser

type_name = 'PLACEMENT'
class Placement(geometric_representation_item.GeometricRepresentationItem):
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
    location     = {clean_display(self.location)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.location = CartesianPoint(parser, args[1])
    
child_type_register = ChildTypeRegister(type_name, geometric_representation_item.child_type_register)
child_type_register.register(type_name, lambda parser, key: Placement(parser, key))