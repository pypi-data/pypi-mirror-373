from .helpers import clean_display_list
from .surface_style_fill_area import SurfaceStyleFillArea
from .abstract_types import surface_style_register
from ..step_parser import StepParser

class SurfaceSideStyle():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''SURFACE_SIDE_STYLE (
    key          = {self.key}
    side         = {self.side}
    styles       = {clean_display_list(self.styles)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.side = args[0]
        self.styles = [surface_style_register.parse(parser, e) for e in args[1]]