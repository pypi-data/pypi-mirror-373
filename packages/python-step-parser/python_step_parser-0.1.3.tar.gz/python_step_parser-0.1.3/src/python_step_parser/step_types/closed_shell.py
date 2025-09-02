from .helpers import clean_display_list
from .advanced_face import AdvancedFace
from .transient import Transient
from ..step_parser import StepParser

class ClosedShell(Transient):
    type_name = 'CLOSED_SHELL'

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
    name         = {self.name}
    faces        = {clean_display_list(self.faces)} '''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.faces = [AdvancedFace(parser, arg) for arg in args[1]]

    def get_geometry(self):
        return super().get_geometry() | {
            'faces': [f.get_geometry() for f in self.faces]
        }