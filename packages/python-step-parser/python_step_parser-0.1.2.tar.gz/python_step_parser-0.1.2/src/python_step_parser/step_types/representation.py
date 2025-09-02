from .helpers import clean_display, clean_display_list
from ..child_type_register import ChildTypeRegister
from . import representation_item
from . import transient
from . import representation_context
from ..step_parser import StepParser

type_name = 'REPRESENTATION'
class Representation(transient.Transient):
    type_name = type_name
    def __init__(self, parser: StepParser, key: int, resolve_children: bool = False):
        super().__init__(parser, key, resolve_children)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    name         = {self.name}
    items        = {clean_display_list(self.items) if self.resolve_children else self.items}
    context      = {clean_display(self.context) if self.resolve_children else self.context}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)

        self.name = args[0]
        if self.resolve_children:
            self.items = [representation_item.child_type_register.parse(parser, a) for a in args[1]]
        else:
            self.items = args[1]
        
        self.context = representation_context.child_type_register.parse(parser, args[2])

child_type_register = ChildTypeRegister(type_name, transient.child_type_register)
child_type_register.register(type_name, lambda parser, key: Representation(parser, key))