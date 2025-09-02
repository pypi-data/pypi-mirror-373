from .helpers import clean_display
from . import application_context_element
from ..step_parser import StepParser

class ProductDefinitionContext(application_context_element.ApplicationContextElement):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''PRODUCT_DEFINITION_CONTEXT (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    stage        = {self.life_cycle_stage}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.life_cycle_stage = args[2]

application_context_element.register(
    'PRODUCT_DEFINITION_CONTEXT',
    lambda parser, key: ProductDefinitionContext(parser, key)
)
