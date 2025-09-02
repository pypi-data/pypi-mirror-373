from .helpers import clean_display, clean_display_list
from .transient import Transient
from ..step_parser import StepParser

class ProductDefinitionRelationship(Transient):
    def __init__(self, parser: StepParser, key: int):
        super().__init__(parser, key)
        self.__get_arguments(parser)

    def __str__(self):
        return f'''PRODUDCT_DEFINITION_RELATIONSHIP (
{self._str_args()}
)
'''
    
    def _str_args(self):
        return f'''{super()._str_args()}
    id           = {self.id}
    name         = {self.name}
    description  = {self.description}
    relating_def = {self.relating_product_definition}
    related_def  = {self.related_product_definition}'''
    
    def __get_arguments(self, parser: StepParser):
        args = parser.get_arguments(self.key)
        
        self.id = args[0]
        self.name = args[1]
        self.description = args[2]
        self.relating_product_definition = args[3]
        self.related_product_definition = args[4]