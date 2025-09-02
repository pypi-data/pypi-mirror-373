from ..child_type_register import ChildTypeRegister
from . import transient
from ..step_parser import StepParser

type_name = 'REPRESENTATION_CONTEXT'
class RepresentationContext(transient.Transient):
    type_name = type_name
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
    context_id   = {self.context_identifier}
    context_type = {self.context_type}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_CONTEXT',])
        
        self.context_identifier = args[0]
        self.context_type = args[1]

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: RepresentationContext(parser, key))