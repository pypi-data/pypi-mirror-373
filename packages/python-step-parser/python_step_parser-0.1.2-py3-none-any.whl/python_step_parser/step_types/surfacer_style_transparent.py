
from ..step_parser import StepParser

class SurfaceStyleTransparent():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''SURFACE_STYLE_TRANSPARENT (
    key          = {self.key}
    transparency = {self.transparency}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.transparency = args[0]