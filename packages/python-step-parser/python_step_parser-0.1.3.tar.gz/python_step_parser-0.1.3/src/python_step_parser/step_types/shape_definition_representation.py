from .helpers import clean_display
from . import shape_definition
from . import property_definition
from . import shape_representation
from ..step_parser import StepParser

type_name = 'SHAPE_DEFINITION_REPRESENTATION'
class ShapeDefinitionRepresentation(shape_definition.ShapeDefinition):
    def __init__(self, parser: StepParser, key: int):
        self.key = key
        self.__get_arguments(parser)
        pass

    def __str__(self):
        return f'''{type_name} (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    shape        = {clean_display(self.shape)}
    rep          = {clean_display(self.representation)}'''

    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        self.shape = property_definition.child_type_register.parse(parser, args[0])
        self.representation = shape_representation.child_type_register.parse(parser, args[1])

shape_definition.child_type_register.register(type_name, lambda parser, key: ShapeDefinitionRepresentation(parser, key))