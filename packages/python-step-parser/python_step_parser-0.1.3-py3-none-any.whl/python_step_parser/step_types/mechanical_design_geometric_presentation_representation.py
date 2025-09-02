from ..child_type_register import ChildTypeRegister
from . import presentation_representation
from ..step_parser import StepParser

type_name = 'MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION'

class MechanicalDesignGeometricPresentationRepresentation(presentation_representation.PresentationRepresentation):
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
        return f'''{super()._str_args()}'''
    
    def __get_arguments(self, parser: StepParser):
        pass


presentation_representation.child_type_register.register(type_name, lambda parser, key: MechanicalDesignGeometricPresentationRepresentation(parser, key))