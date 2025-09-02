from typing import Dict, Callable, Any
from .step_parser import StepParser

class ChildTypeRegister():
    def __init__(self, name, base_registers=None):
        self.name = name
        self.base_registers = base_registers
        self.child_type_register: Dict[str, Callable[[StepParser, int], Any]] = {}

    def try_parse(self, parser: StepParser, id: int):
        type = parser.get_entity_type(id)
        if type == 'COMPLEX':
            complex_items = parser.get_complex_items(id)
            complex_item_types = [i.type for i in complex_items]
            for resolved_type in complex_item_types:
                if resolved_type in self.child_type_register:
                    # print('resolving', id, 'as', resolved_type)
                    return self.child_type_register[resolved_type](parser, id)
            return None
        if type in self.child_type_register:
            return self.child_type_register[type](parser, id)
        return None

    def parse(self, parser: StepParser, id: int):
        type = parser.get_entity_type(id)
        if type == 'COMPLEX':
            complex_items = parser.get_complex_items(id)
            complex_item_types = [i.type for i in complex_items]
            for resolved_type in complex_item_types:
                if resolved_type in self.child_type_register:
                    # print('resolving', id, 'as', resolved_type)
                    return self.child_type_register[resolved_type](parser, id)
            raise Exception(f'Cannot find context with type {type} [{','.join(complex_item_types)}]')
        if type in self.child_type_register:
            return self.child_type_register[type](parser, id)
        raise Exception(f'Cannot find {self.name} with type {type}')
    
    def register(self, type_name: str, type_val):
        self.child_type_register[type_name] = type_val
        if self.base_registers is not None:
            if isinstance(self.base_registers, list):
                for r in self.base_registers:
                    r.register(type_name, type_val)
            else:
                self.base_registers.register(type_name, type_val)
