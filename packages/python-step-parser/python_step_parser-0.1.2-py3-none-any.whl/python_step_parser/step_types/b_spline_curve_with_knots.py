from ..child_type_register import ChildTypeRegister
from . import b_spline_curve
from ..step_parser import StepParser

type_name = 'B_SPLINE_CURVE_WITH_KNOTS'
class BSplineCurveWithKnots(b_spline_curve.BSPlineCurve):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{self.type_name} (
{self._str_args()}
)
'''

    def _str_args(self):
        return f'''{super()._str_args()}
    knot_mult    = {self.knot_multiplicities}
    knots        = {self.knots}
    knot_spec    = {self.knot_spec}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(self.key,
                                                    ['REPRESENTATION_ITEM',
                                                     'GEOMETRIC_REPRESENTATION_ITEM',
                                                     'CURVE',
                                                     'BOUNDED_CURVE',
                                                     'B_SPLINE_CURVE',
                                                     'B_SPLINE_CURVE_WITH_KNOTS'])
        
        self.knot_multiplicities = args[6]
        self.knots = args[7]
        self.knot_spec = args[8]
        
    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'knot_mult': [int(v) for v in self.knot_multiplicities],
            'knots': [float(v) for v in self.knots],
            'spec': self.knot_spec
        }
    
    
child_type_register = ChildTypeRegister(type_name, b_spline_curve.child_type_register)
child_type_register.register(type_name, lambda parser, key: BSplineCurveWithKnots(parser, key))