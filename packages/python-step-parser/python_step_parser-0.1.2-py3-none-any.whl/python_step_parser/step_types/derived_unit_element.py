from .helpers import clean_display
from . import transient
from . import named_unit
from .abstract_types import unit_register
from ..step_parser import StepParser

type_name = 'DERIVED_UNIT_ELEMENT'
class DerivedUnitElement(transient.Transient):
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
    unit         = {clean_display(self.unit)}
    exponent     = {self.exponent}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.unit = named_unit.child_type_register.parse(parser, args[0])
        self.exponent = args[1]

transient.child_type_register.register(type_name, lambda parser, key: DerivedUnitElement(parser, key))