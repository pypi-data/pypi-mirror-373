from .helpers import clean_display, clean_display_list
from .face_bound import FaceBound
from .transient import Transient, child_type_register
from .surface import child_type_register as surface_type_register
from ..step_parser import StepParser

type_name = 'ADVANCED_FACE'
class AdvancedFace(Transient):
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
    name         = {self.name}
    bounds       = {clean_display_list(self.bounds)}
    geometry     = {clean_display(self.geometry)}
    same_sense   = {self.same_sense}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.bounds = [FaceBound(parser, b) for b in args[1]]
        self.geometry = surface_type_register.parse(parser, args[2])
        self.same_sense = args[3]

    def get_geometry(self):
        return super().get_geometry() | {
            'bounds': [b.get_geometry() for b in self.bounds],
            'surface': self.geometry.get_geometry()
        }
    
child_type_register.register(type_name, lambda parser, key: AdvancedFace(parser, key))