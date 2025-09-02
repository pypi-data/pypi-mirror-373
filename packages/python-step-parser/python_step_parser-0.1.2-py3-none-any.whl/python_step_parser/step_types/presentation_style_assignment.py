from .helpers import clean_display_list
from .surface_style_usage import SurfaceStyleUsage
from ..step_parser import StepParser

class PresentationStyleAssignment():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''PRESENTATION_STYLE_ASSIGNMENT (
    key          = {self.key}
    styles       = {clean_display_list(self.styles)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.styles = [SurfaceStyleUsage(parser, e) for e in args[0]]