from typing import List, Union, Tuple, Dict, Any
import re
import itertools
from .complex_item_dto import ComplexItemDTO

def split_arguments(arg_string: str) -> List[str]:
    """Splits arguments while handling parentheses (nested lists)."""
    args = []
    depth = 0
    escaped = None 
    current = ''
    for char in arg_string:
        if escaped is None and char == "'":
            escaped = char
            current += char
        elif escaped == char:
            escaped = None
            current += char
        elif escaped is None and char == ',' and depth == 0:
            args.append(current.strip())
            current = ''
        else:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            current += char
    if current:
        args.append(current.strip())
    return args

def classify_arg(arg: str) -> Tuple[str, Union[str, None]]:
    """Returns (type, value_text) for an argument."""
    arg = arg.strip()
    if not arg or arg == '$':
        return 'null', None
    if arg.startswith("'") and arg.endswith("'"):
        return 'string', arg.strip("'")
    if re.match(r'^#\d+$', arg):
        return 'reference', arg[1:]  # store just the ID number
    if arg.startswith('(') and arg.endswith(')'):
        return 'list', arg  # will be handled separately
    if re.match(r'^-?\d+(\.\d+)?$', arg):
        return 'number', arg
    return 'string', arg.strip("'")  # fallback

def parse_arg_value(value_type: str, value_text: str) -> Any:
    if value_type == 'list':
        return [int(v[1:]) if v[0] == '#' else v
                for v
                in [v.strip()
                    for v
                    in value_text[1:len(value_text)-1].split(',')]]
    if value_type == 'reference':
        return int(value_text)
    if value_type == 'number':
        return float(value_text)
    return value_text

def get_complex_args(args: List[str], types: List[ComplexItemDTO], type_name: str) -> List[str]:
    ci = next((t for t in types if t.type == type_name), None)
    if ci is None:
        return []
    return args[ci.arg_offset:(ci.arg_offset + ci.n_args)]

def get_all_complex_args(args: List[str], types: List[ComplexItemDTO], type_names: List[str]) -> List[str]:
    return list(itertools.chain.from_iterable([
        get_complex_args(args, types, t)
        for t in type_names
    ]))
