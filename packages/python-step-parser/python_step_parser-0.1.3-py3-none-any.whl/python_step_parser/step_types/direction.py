
from ..step_parser import StepParser

class Direction():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''DIRECTION (
    key          = {self.key}
    name         = {self.name}
    dir_ratios   = {self.direction_ratios}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.direction_ratios = args[1]

    def get_geometry(self):
        x,y,z = self.direction_ratios
        return [float(x), float(y), float(z)]