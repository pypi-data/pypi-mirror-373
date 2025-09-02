from .helpers import clean_display, clean_display_list
from .presentation_style_assignment import PresentationStyleAssignment
from . import representation_item
from . import transient
from ..step_parser import StepParser
from ..child_type_register import ChildTypeRegister

type_name = 'STYLED_ITEM'

class StyledItem(representation_item.RepresentationItem):
    type_name = type_name

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
    styles       = {clean_display_list(self.styles)}
    item         = {clean_display(self.item)}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.styles = [PresentationStyleAssignment(parser, e) for e in args[1]]
        self.item = transient.child_type_register.parse(parser, args[2])


child_type_register = ChildTypeRegister(type_name, representation_item.child_type_register)
child_type_register.register(type_name, lambda parser, key: StyledItem(parser, key))