from .helpers import clean_display
from .surface_side_style import SurfaceSideStyle
from ..step_parser import StepParser

class SurfaceStyleUsage():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''SURFACE_STYLE_USAGE (
    key          = {self.key}
    side         = {self.side}
    style        = {clean_display(self.style)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.side = args[0]
        self.style = SurfaceSideStyle(parser, args[1])