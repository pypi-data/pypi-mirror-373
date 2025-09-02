from .helpers import clean_display, clean_display_list
from .product_definition_usage import ProductDefinitionUsage
from ..step_parser import StepParser

class AssemblyComponentUsage(ProductDefinitionUsage):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''ASSEMBLY_COMPONENT_USAGE (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    designator   = {self.reference_designator}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.reference_designator = args[5]