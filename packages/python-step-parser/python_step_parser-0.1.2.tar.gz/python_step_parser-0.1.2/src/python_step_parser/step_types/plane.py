from .helpers import clean_display
from . import elementary_surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class Plane(elementary_surface.ElementarySurface):
    type_name = 'PLANE'

    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{self.type_name} (
{self._str_args()}
)
'''

    def _str_args(self):
        return f'''{super()._str_args()}'''
    
    def __get_arguments(self, parser: StepParser):
        pass

child_type_register = ChildTypeRegister('PLANE', elementary_surface.child_type_register)
child_type_register.register('PLANE', lambda parser, key: Plane(parser, key))