from ..child_type_register import ChildTypeRegister
from . import application_context_element
from ..step_parser import StepParser

type_name = 'PRODUCT_CONTEXT'
class ProductContext(application_context_element.ApplicationContextElement):
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
    discipline   = {self.discipline}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.discipline = args[2]

child_type_register = ChildTypeRegister(type_name, application_context_element.child_type_register)
child_type_register.register(type_name, lambda parser, key: ProductContext(parser, key))