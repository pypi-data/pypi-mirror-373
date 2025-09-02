from ..child_type_register import ChildTypeRegister
from . import product_definition_formation
from ..step_parser import StepParser

type_name: str = 'PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE'
class ProductDefinitionFormationWithSource(product_definition_formation.ProductDefinitionFormation):
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
    source       = {self.source}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.source = args[3]

child_type_register = ChildTypeRegister(type_name, product_definition_formation.child_type_register)
child_type_register.register(type_name, lambda parser, key: ProductDefinitionFormationWithSource(parser, key))
