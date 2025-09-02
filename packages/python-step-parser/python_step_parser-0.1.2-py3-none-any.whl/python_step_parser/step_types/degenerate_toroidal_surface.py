from .helpers import clean_display
from . import toroidal_surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class DegenerateToroidalSurface(toroidal_surface.ToroidalSurface):
    type_name = 'DEGENERATE_TOROIDAL_SURFACE'

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
    select_outer = {self.select_outer}'''

    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.select_outer = args[4]
    
child_type_register = ChildTypeRegister('DEGENERATE_TOROIDAL_SURFACE', toroidal_surface.child_type_register)
child_type_register.register('DEGENERATE_TOROIDAL_SURFACE', lambda parser, key: DegenerateToroidalSurface(parser, key))