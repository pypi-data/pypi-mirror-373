from ..child_type_register import ChildTypeRegister
from ..step_parser import StepParser

class Transient():
    type_name: str = 'TRANSIENT'

    def __init__(self, parser: StepParser, key: int, resolve_children: bool = True):
        self.key = key
        self.resolve_children = resolve_children

    def __str__(self):
        return f'''{self.type_name} (
{self._str_args()}
)
'''
    def _str_args(self):
        return f'''    key          = {self.key}'''
    
    def __get_arguments(self, parser: StepParser):
        pass
    
    def get_geometry(self):
        return {}
    
child_type_register = ChildTypeRegister('Transient')
