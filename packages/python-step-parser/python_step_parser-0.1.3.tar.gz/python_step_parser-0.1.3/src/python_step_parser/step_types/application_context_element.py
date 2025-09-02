from ..child_type_register import ChildTypeRegister
from . import transient 
from . import application_context
from ..step_parser import StepParser

type_name = 'APPLICATION_CONTEXT_ELEMENT'
class ApplicationContextElement(transient.Transient):
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
    name         = {self.name}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.name = args[0]
        self.context = application_context.child_type_register.parse(parser, args[1])

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: ApplicationContextElement(parser, key))
