from .helpers import clean_display
from .axis2_placement3d import Axis2Placement3d
from . import curve
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class Conic(curve.Curve):
    type_name = 'CONIC'

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
    position     = {clean_display(self.position)}'''

    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.position = Axis2Placement3d(parser, args[1])

child_type_register = ChildTypeRegister('CONIC', curve.child_type_register)
child_type_register.register('CONIC', lambda parser, key: Conic(parser, key))