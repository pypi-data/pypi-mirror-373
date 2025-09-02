from ..child_type_register import ChildTypeRegister
from . import transient
from ..step_parser import StepParser

type_name = 'SHAPE_DEFINITION'
class ShapeDefinition(transient.Transient):
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        pass

        
child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: ShapeDefinition(parser, key))