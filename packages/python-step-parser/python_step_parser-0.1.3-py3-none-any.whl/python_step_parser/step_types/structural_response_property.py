from .product_definition import ProductDefinition
from ..step_parser import StepParser

class StructuralResponseProperty(ProductDefinition):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''STRUCTURAL_RESPONSE_PROPERTY (
{self._str_args()}    
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}'''
    
    def __get_arguments(self, parser: StepParser):
        # No special arguments
        pass