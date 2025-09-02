from .helpers import clean_display
from ..child_type_register import ChildTypeRegister
from .closed_shell import ClosedShell
from . import solid_model
from ..step_parser import StepParser

type_name = 'MANIFOLD_SOLID_BREP'
class ManifoldSolidBrep(solid_model.SolidModel):
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
    outer        =  {clean_display(self.outer) if self.resolve_children else self.outer}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        if self.resolve_children:
            self.outer = ClosedShell(parser, args[1])
        else:
            self.outer = args[1]

child_type_register = ChildTypeRegister(type_name, solid_model.child_type_register)
child_type_register.register(type_name, lambda parser, key: ManifoldSolidBrep(parser, key))