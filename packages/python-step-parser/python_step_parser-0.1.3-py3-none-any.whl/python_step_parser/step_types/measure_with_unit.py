from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from .abstract_types import unit_register
from . import transient
from ..step_parser import StepParser

type_name = 'MEASURE_WITH_UNIT'
class MeasureWithUnit(transient.Transient):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''type_name (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    value        = {self.value}
    unit         = {clean_display(self.context)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.value = args[0]
        self.unit = unit_register.parse(parser, args[1])


child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: MeasureWithUnit(parser, key))