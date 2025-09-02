from .helpers import clean_display
from .topological_representation_item import TopologicalRepresentationItem
from ..step_parser import StepParser

class Edge(TopologicalRepresentationItem):
    type_name = 'EDGE'

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