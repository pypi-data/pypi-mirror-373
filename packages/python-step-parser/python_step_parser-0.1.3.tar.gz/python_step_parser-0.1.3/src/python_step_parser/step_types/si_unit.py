from ..child_type_register import ChildTypeRegister
from . import named_unit
from ..step_parser import StepParser

type_name = 'SI_UNIT'
class SIUnit(named_unit.NamedUnit):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''SI_UNIT (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    prefix       = {self.prefix}
    name         = {self.name}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['NAMED_UNIT',
                                              'SI_UNIT'])
        
        self.prefix = args[1]
        self.name = args[2]

child_type_register = ChildTypeRegister(type_name, named_unit.child_type_register)
child_type_register.register(type_name, lambda parser, key: SIUnit(parser, key))