from .helpers import clean_display
from . import conic
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class Circle(conic.Conic):
    type_name = 'CIRCLE'

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
            'type': self.type_name,
            'radius': self.radius,
        }

child_type_register = ChildTypeRegister('CIRCLE', conic.child_type_register)
child_type_register.register('CIRCLE', lambda parser, key: Circle(parser, key))