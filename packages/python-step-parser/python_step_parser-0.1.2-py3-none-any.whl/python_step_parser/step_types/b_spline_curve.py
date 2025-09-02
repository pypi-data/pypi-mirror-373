from .helpers import clean_display_list
from ..child_type_register import ChildTypeRegister
from . import bounded_curve
from .cartesian_point import CartesianPoint
from ..step_parser import StepParser

type_name = 'B_SPLINE_CURVE'

class BSPlineCurve(bounded_curve.BoundedCurve):
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
    degree       = {self.degree}
    control_pts  = {clean_display_list(self.control_points_list)}
    curve_form   = {self.curve_form}
    closed_curve = {self.closed_curve}
    self_insect  = {self.self_intersect}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(self.key,
                                                    ['REPRESENTATION_ITEM',
                                                     'GEOMETRIC_REPRESENTATION_ITEM',
                                                     'CURVE',
                                                     'BOUNDED_CURVE',
                                                     'B_SPLINE_CURVE'])
        
        self.degree = args[1]
        self.control_points_list = [CartesianPoint(parser, p) for p in args[2]]
        self.curve_form = args[3]
        self.closed_curve = args[4]
        self.self_intersect = args[5]

    def get_geometry(self):
        return super().get_geometry() | {
            'type': self.type_name,
            'deg': self.degree,
            'ctrl': [p.get_geometry() for p in self.control_points_list],
            'form': self.curve_form,
            'is_closed': self.closed_curve,
            'is_self_insersect': self.self_intersect
        }
    
child_type_register = ChildTypeRegister(type_name, bounded_curve.child_type_register)
child_type_register.register(type_name, lambda parser, key: BSPlineCurve(parser, key))