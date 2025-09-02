from ..child_type_register import ChildTypeRegister
from . import transient
from ..step_parser import StepParser

type_name = 'REPRESENTATION_ITEM'
class RepresentationItem(transient.Transient):
    type_name = type_name

    def __init__(self, parser: StepParser, key: int, resolve_children: bool = False):
        super().__init__(parser, key, resolve_children)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{self.type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    name         = {self.name}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_ITEM'])
        self.name = args[0]


child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: RepresentationItem(parser, key))