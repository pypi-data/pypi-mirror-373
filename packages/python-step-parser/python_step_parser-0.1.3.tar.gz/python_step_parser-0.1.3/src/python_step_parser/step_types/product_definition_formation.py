from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from . import transient
from . import product
from ..step_parser import StepParser

type_name: str = 'PRODUCT_DEFINITION_FORMATION'
class ProductDefinitionFormation(transient.Transient):
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
    id           = {self.id}
    description  = {self.description}
    product      = {clean_display(self.product)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.id = args[0]
        self.description = args[1]
        self.product = product.child_type_register.parse(parser, args[2])

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: ProductDefinitionFormation(parser, key))
