from .helpers import clean_display
from . import surface
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class BoundedSurface(surface.Surface):
    type_name = 'BOUNDED_SURFACE'

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

    def get_geometry(self):
        return {
            'type': 'BOUNDED'
        }

child_type_register = ChildTypeRegister('BOUNDED_SURFACE', surface.child_type_register)
child_type_register.register('BOUNDED_SURFACE', lambda parser, key: BoundedSurface(parser, key))