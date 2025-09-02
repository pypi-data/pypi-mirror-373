from ..child_type_register import ChildTypeRegister
from . import representation_context
from ..step_parser import StepParser

type_name = 'GEOMETRIC_REPRESENTATION_CONTEXT'
class GeometricRepresentationContext(representation_context.RepresentationContext):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    dimension    = {self.dimension}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_complex_or_base_arguments(
                                             self.key,
                                             ['REPRESENTATION_CONTEXT',
                                              'GEOMETRIC_REPRESENTATION_CONTEXT'])
        
        self.dimension = args[2]

child_type_register = ChildTypeRegister(type_name, representation_context.child_type_register)
child_type_register.register(type_name, lambda parser, key: GeometricRepresentationContext(parser, key))