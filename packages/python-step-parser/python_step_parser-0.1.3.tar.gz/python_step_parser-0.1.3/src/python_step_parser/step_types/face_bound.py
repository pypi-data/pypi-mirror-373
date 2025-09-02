from .helpers import clean_display
from .topological_representation_item import TopologicalRepresentationItem
from ..step_parser import StepParser
from . import loop

class FaceBound(TopologicalRepresentationItem):
    type_name = 'FACE_BOUND'

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
    bound        = {clean_display(self.bound)}
    orientation  = {self.orientation}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.bound = loop.child_type_register.parse(parser, args[1])
        self.orientation = args[2]
    
    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'bound': self.bound.get_geometry(),
            'orientation': self.orientation
        }