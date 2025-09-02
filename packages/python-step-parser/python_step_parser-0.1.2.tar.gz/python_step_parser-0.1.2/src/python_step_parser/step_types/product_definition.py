from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from . import transient
from . import abstract_types
from . import product_definition_formation
from ..step_parser import StepParser

type_name = 'PRODUCT_DEFINITION'
class ProductDefinition(transient.Transient):
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
    formation    = {clean_display(self.formation)}
    context      = {clean_display(self.context)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.id = args[0]
        self.description = args[1]
        self.formation = product_definition_formation.child_type_register.parse(parser, args[2])
        self.context = args[3]

child_type_register = ChildTypeRegister(type_name, [
    transient.child_type_register,
    abstract_types.characterized_definition_register
])
child_type_register.register(type_name, lambda parser, key: ProductDefinition(parser, key))