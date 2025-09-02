from .helpers import clean_display_doublelist
from . import bounded_surface
from .cartesian_point import CartesianPoint
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

class BSPlineSurface(bounded_surface.BoundedSurface):
    type_name = 'B_SPLINE_SURFACE'

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
    udegree      = {self.udegree}
    vdegree      = {self.vdegree}
    control_pts  = {clean_display_doublelist(self.control_points_list)}
    surface_form = {self.surface_form}
    uclosed      = {self.uclosed}
    vclosed      = {self.vclosed}
    self_insect  = {self.self_intersect}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)

        self.udegree = args[1]
        self.vdegree = args[2]
        self.control_points_list = [[CartesianPoint(parser, p) for p in ps] for ps in args[3]]
        self.surface_form = args[4]
        self.uclosed = args[5]
        self.vclosed = args[6]
        self.self_intersect = args[7]

child_type_register = ChildTypeRegister('B_SPLINE_SURFACE', bounded_surface.child_type_register)
child_type_register.register('B_SPLINE_SURFACE', lambda parser, key: BSPlineSurface(parser, key))