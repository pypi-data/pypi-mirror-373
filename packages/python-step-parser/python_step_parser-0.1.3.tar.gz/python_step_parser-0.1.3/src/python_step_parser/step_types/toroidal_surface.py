from .helpers import clean_display
from . import elementary_surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class ToroidalSurface(elementary_surface.ElementarySurface):
    type_name = 'TOROIDAL_SURFACE'

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
    major_radius = {self.major_radius}
    minor_radius = {self.minor_radius}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.major_radius = args[2]
        self.minor_radius = args[3]

child_type_register = ChildTypeRegister('TOROIDAL_SURFACE', elementary_surface.child_type_register)
child_type_register.register('TOROIDAL_SURFACE', lambda parser, key: ToroidalSurface(parser, key))