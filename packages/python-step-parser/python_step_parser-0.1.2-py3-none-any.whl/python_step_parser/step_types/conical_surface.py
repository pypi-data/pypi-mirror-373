from .helpers import clean_display
from . import elementary_surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class ConicalSurface(elementary_surface.ElementarySurface):
    type_name = 'CONICAL_SURFACE'

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
    radius       = {self.radius}
    semi_angle   = {self.semi_angle}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.radius = args[2]
        self.semi_angle = args[3]

        
child_type_register = ChildTypeRegister('CONICAL_SURFACE', elementary_surface.child_type_register)
child_type_register.register('CONICAL_SURFACE', lambda parser, key: ConicalSurface(parser, key))