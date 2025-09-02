from .helpers import clean_display, clean_display_list
from .assembly_component_usage import AssemblyComponentUsage 
from ..step_parser import StepParser

class NextAssemblyUsageOccurrence(AssemblyComponentUsage):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''NEXT_ASSEMBLY_USAGE_OCCURRENCE (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'{super()._str_args()}'
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        # No additional args