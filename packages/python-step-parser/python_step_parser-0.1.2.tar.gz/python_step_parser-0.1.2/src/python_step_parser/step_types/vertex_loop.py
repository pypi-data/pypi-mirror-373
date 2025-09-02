from .helpers import clean_display
from .vertex_point import VertexPoint
from . import loop
from ..step_parser import StepParser

type_name = 'VERTEX_LOOP'
class VertexLoop(loop.Loop):
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
    vertex       = {clean_display(self.vertex)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.vertex = VertexPoint(parser, args[1])

loop.child_type_register.register(type_name, lambda parser, key: VertexLoop(parser, key))