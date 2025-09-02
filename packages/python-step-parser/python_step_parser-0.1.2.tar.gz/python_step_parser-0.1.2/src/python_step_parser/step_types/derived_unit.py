from .helpers import clean_display_list
from . import transient
from . import derived_unit_element
from .abstract_types import unit_register
from ..step_parser import StepParser

type_name = 'DERIVED_UNIT'
class DerivedUnit(transient.Transient):
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
    elements     = {clean_display_list(self.elements)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.elements = [derived_unit_element.DerivedUnitElement(parser, arg) for arg in args[0]]

transient.child_type_register.register(type_name, lambda parser, key: DerivedUnit(parser, key))
unit_register.register(type_name, lambda parser, key: DerivedUnit(parser, key))