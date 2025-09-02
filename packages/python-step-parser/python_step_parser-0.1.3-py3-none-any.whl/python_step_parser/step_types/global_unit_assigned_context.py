from .helpers import clean_display_list
from ..child_type_register import ChildTypeRegister
from . import representation_context
from . import si_unit
from ..step_parser import StepParser

type_name = 'GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT'
class GlobalUncertaintyAssignedContext(representation_context.RepresentationContext):
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
    units        = {clean_display_list(self.units)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_CONTEXT',
                                              'GLOBAL_UNIT_ASSIGNED_CONTEXT'])
        
        self.units = [si_unit.child_type_register.parse(parser, a) for a in args[2]]

child_type_register = ChildTypeRegister(type_name, representation_context.child_type_register)
child_type_register.register(type_name, lambda parser, key: GlobalUncertaintyAssignedContext(parser, key))