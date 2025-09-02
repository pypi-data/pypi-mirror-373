from .helpers import clean_display_list
from ..child_type_register import ChildTypeRegister
from . import transient
from . import product_context
from ..step_parser import StepParser

type_name: str = 'PRODUCT'

class Product(transient.Transient):
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
    name         = {self.name}
    description  = {self.description}
    product_ctxs = {clean_display_list(self.product_contexts)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.id = args[0]
        self.name = args[1]
        self.description = args[2]
        self.product_contexts = [product_context.child_type_register.parse(parser, i) for i in args[3]]

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: Product(parser, key))