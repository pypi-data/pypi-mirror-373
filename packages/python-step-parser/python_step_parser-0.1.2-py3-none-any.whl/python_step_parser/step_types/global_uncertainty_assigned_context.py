
from .representation_context import RepresentationContext
from ..step_parser import StepParser

class GlobalUncertaintyAssignedContext(RepresentationContext):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    uncertainty  = {self.uncertainty}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_CONTEXT',
                                              'GEOMETRIC_REGLOBAL_UNCERTAINTY_ASSIGNED_CONTEXTPRESENTATION_CONTEXT'])
        
        self.uncertainty = args[2]
