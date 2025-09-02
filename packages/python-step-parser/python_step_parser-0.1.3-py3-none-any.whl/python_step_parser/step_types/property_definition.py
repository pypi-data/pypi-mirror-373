from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from . import transient
from . import product_definition_formation
from . import abstract_types
from ..step_parser import StepParser

type_name = 'PROPERTY_DEFINITION'
class PropertyDefinition(transient.Transient):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    name         = {self.name}
    description  = {self.description}
    definition   = {clean_display(self.definition)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.name = args[0]
        self.description = args[1]
        self.definition = abstract_types.characterized_definition_register.parse(parser, args[2])

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: PropertyDefinition(parser, key))