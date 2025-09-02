from ..child_type_register import ChildTypeRegister
from . import property_definition
from .abstract_types import characterized_definition_register
from ..step_parser import StepParser

type_name = 'PRODUCT_DEFINITION_SHAPE'
class ProductDefinitionShape(property_definition.PropertyDefinition):
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
        # No special arguments
        pass

child_type_register = ChildTypeRegister(type_name, [
    property_definition.child_type_register,
    characterized_definition_register
])
child_type_register.register(type_name, lambda parser, key: ProductDefinitionShape(parser, key))