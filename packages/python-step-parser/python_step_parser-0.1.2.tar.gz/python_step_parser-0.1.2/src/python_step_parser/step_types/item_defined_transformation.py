from .helpers import clean_display
from .axis2_placement3d import Axis2Placement3d
from ..step_parser import StepParser

class ItemDefinedTransformation():
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''ITEM_DEFINED_TRANSFORMATION (
    key          = {self.key}
    name         = {self.name}
    description  = {self.description}
    trans_item1  = {clean_display(self.trans_item1)}
    trans_item2  = {clean_display(self.trans_item2)}
)
'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.name = args[0]
        self.description = args[1]
        self.trans_item1 = Axis2Placement3d(parser, args[2])
        self.trans_item2 = Axis2Placement3d(parser, args[3])