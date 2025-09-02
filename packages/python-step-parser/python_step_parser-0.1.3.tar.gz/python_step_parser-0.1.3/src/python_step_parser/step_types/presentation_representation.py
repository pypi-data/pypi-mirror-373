from ..child_type_register import ChildTypeRegister
from . import representation
from ..step_parser import StepParser

type_name = 'PRESENTATION_REPRESENTATION'
class PresentationRepresentation(representation.Representation):
    type_name = type_name

    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
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

child_type_register = ChildTypeRegister(type_name, representation.child_type_register)
child_type_register.register(type_name, lambda parser, key: PresentationRepresentation(parser, key))