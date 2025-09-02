from .helpers import clean_display
from . import elementary_surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class CylindricalSurface(elementary_surface.ElementarySurface):
    type_name = 'CYLINDRICAL_SURFACE'

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
    radius       = {self.radius}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.radius = args[2]
        
    def get_geometry(self):
        return super().get_geometry() | {
            'type': 'CYLINDRICAL',
            'radius': self.radius
        }
    
child_type_register = ChildTypeRegister('CYLINDRICAL_SURFACE', elementary_surface.child_type_register)
child_type_register.register('CYLINDRICAL_SURFACE', lambda parser, key: CylindricalSurface(parser, key))