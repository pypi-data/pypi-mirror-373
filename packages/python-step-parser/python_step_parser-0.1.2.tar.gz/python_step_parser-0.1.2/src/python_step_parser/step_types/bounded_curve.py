from ..child_type_register import ChildTypeRegister
from . import curve
from ..step_parser import StepParser

type_name = 'BOUNDED_CURVE'

class BoundedCurve(curve.Curve):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''

    def _str_args(self):
        return f'''{super()._str_args()}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_ITEM',
                                              'GEOMETRIC_REPRESENTATION_ITEM',
                                              'CURVE',
                                              'BOUNDED_CURVE'])
        pass

    def get_geometry(self):
        return {
            'type': 'BOUNDED_CURVE'
        }
    
child_type_register = ChildTypeRegister(type_name, curve.child_type_register)
child_type_register.register(type_name, lambda parser, key: BoundedCurve(parser, key))