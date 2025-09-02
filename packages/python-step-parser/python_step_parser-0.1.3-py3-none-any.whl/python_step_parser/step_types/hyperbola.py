from .helpers import clean_display
from .conic import Conic
from ..step_parser import StepParser

class Hyperbola(Conic):
    type_name = 'HYPERBOLA'

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
    semi_axis    = {self.semi_axis}
    semi_axis_i  = {self.semi_imag_axis}'''

    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.semi_axis = args[2]
        self.semi_imag_axis = args[3]

    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'axes': [self.semi_axis, self.semi_imag_axis],
        }