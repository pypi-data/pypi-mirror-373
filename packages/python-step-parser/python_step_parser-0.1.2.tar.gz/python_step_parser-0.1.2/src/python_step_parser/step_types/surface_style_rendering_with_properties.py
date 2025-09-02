from .helpers import clean_display, clean_display_list
from .abstract_types import color_register
from .surfacer_style_transparent import SurfaceStyleTransparent
from .abstract_types import surface_style_register
from ..step_parser import StepParser

class SurfaceStyleRenderingWithProperties():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''SURFACE_STYLE_RENDERING_WITH_PROPERTIES (
    key          = {self.key}
    method       = {self.method}
    colour       = {clean_display(self.colour)}
    transparency = {clean_display_list(self.transparency)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.method = args[0]
        self.colour = color_register.parse(parser, args[1])
        self.transparency = [SurfaceStyleTransparent(parser, arg) for arg in args[2]]
        
surface_style_register.register('SURFACE_STYLE_RENDERING_WITH_PROPERTIES', lambda parser, key: SurfaceStyleRenderingWithProperties(parser, key))