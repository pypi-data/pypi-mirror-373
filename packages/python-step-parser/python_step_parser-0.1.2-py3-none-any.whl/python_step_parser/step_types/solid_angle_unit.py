
from . import si_unit
from ..step_parser import StepParser

class SolidAngleUnit(si_unit.SIUnit):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''SOLID_ANGLE_UNIT (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['NAMED_UNIT',
                                              'SI_UNIT',
                                              'SOLID_ANGLE_UNIT'])
        # No extra params
        pass

si_unit.child_type_register.register('SOLID_ANGLE_UNIT', lambda parser, key: SolidAngleUnit(parser, key))