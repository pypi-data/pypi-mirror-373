
from . import si_unit
from ..step_parser import StepParser

class PlaneAngleUnit(si_unit.SIUnit):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''PLANE_ANGLE_UNIT (
{self._str_args()}
)
'''
    
    def _str_args(self):
        super_args = super()._str_args()
        return f'''{super_args}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['NAMED_UNIT',
                                              'SI_UNIT',
                                              'PLANE_ANGLE_UNIT'])
        # No extra params
        pass

si_unit.child_type_register.register('PLANE_ANGLE_UNIT', lambda parser, key: PlaneAngleUnit(parser, key))