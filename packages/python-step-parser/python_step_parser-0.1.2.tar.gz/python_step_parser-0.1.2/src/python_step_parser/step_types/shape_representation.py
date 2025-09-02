from ..child_type_register import ChildTypeRegister
from . import representation
from ..step_parser import StepParser

type_name = 'SHAPE_REPRESENTATION'
class ShapeRepresentation(representation.Representation):
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
        # No special args
        pass

child_type_register = ChildTypeRegister(type_name, representation.child_type_register)
child_type_register.register(type_name, lambda parser, key: ShapeRepresentation(parser, key))