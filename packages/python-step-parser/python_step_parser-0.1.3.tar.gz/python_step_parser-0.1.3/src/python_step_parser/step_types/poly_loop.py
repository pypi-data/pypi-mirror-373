from .helpers import clean_display_list
from .cartesian_point import CartesianPoint
from . import loop
from ..step_parser import StepParser

type_name = 'POLY_LOOP'
class PolyLoop(loop.Loop):
    type_name = type_name

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
    polygon      = {clean_display_list(self.polygon)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.polygon = [CartesianPoint(parser, p) for p in args[1]]
        
loop.child_type_register.register(type_name, lambda parser, key: PolyLoop(parser, key))