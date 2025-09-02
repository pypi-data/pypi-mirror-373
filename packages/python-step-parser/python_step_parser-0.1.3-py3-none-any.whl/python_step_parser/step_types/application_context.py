from ..child_type_register import ChildTypeRegister
from . import transient
from ..step_parser import StepParser

type_name = 'APPLICATION_CONTEXT'
class ApplicationContext(transient.Transient):
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
    application  = {self.application}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.application = args[0]

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: ApplicationContext(parser, key))
