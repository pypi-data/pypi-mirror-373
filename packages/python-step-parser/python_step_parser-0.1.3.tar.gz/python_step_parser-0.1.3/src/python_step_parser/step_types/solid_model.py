from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from . import geometric_representation_item
from . import property_definition
from . import shape_representation
from ..step_parser import StepParser

type_name = 'SOLID_MODEL'
class SolidModel(geometric_representation_item.GeometricRepresentationItem):
    type_name = type_name

    def __init__(self, parser: StepParser, key: int, resolve_children: bool = False):
        super().__init__(parser, key, resolve_children)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}'''

    def __get_arguments(self, parser: StepParser):
        pass

child_type_register = ChildTypeRegister(type_name, geometric_representation_item.child_type_register)
child_type_register.register(type_name, lambda parser, key: SolidModel(parser, key))