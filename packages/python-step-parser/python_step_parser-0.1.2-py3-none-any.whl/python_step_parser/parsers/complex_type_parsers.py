import re
from typing import List, Dict, Union
from .helpers import split_arguments
import itertools

def split_complex_type_entities(complex_type_str: str):
    entities = []
    state = 0
    curr_entity = []

    for v in complex_type_str:
        curr_entity.append(v)

        if state == 0:
            if v == '(':
                state = 1
        elif state > 0:
            if state == 1 and v == ')':
                entities.append(''.join(curr_entity).strip())
                curr_entity = []
                state = 0
            elif v == '(':
                state += 1
            elif v == ')':
                state -= 1
    return entities


# def split_complex_types(entity_types: List[str], entity_args, common_entity_order: List[str], prefix: str):
#     common_indexes = [entity_types.index(e) for e in common_entity_order]
#     common_args = list(itertools.chain.from_iterable([entity_args[i] for i in common_indexes]))
#     if len(entity_types) == len(common_entity_order):
#         return prefix, common_args
#     type_indexes = sorted([i for i in range(0, len(entity_types)) if i not in common_indexes])
#     return (f'{prefix}_AND_{'_AND_'.join([entity_types[i].upper() for i in type_indexes])}',
#             common_args + list(itertools.chain.from_iterable([entity_args[i] for i in type_indexes])))

# def refactor_complex_type(entities: List[object]):
#     entity_types = [e[0] for e in entities]
#     entity_args = [e[1] for e in entities]

#     if 'SI_UNIT' in entity_types:
#         return split_complex_types(entity_types,
#                                    entity_args,
#                                    ['NAMED_UNIT', 'SI_UNIT'],
#                                    'SI_UNIT')
#     if ('REPRESENTATION_CONTEXT' in entity_types
#         and any('COMPONENT_PART' in arg for arg in entity_args[entity_types.index('REPRESENTATION_CONTEXT')])):
#         return split_complex_types(entity_types,
#                                entity_args,
#                                ['REPRESENTATION_CONTEXT',
#                                 'GEOMETRIC_REPRESENTATION_CONTEXT',
#                                 'GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT',
#                                 'GLOBAL_UNIT_ASSIGNED_CONTEXT'],
#                                'COMPONENT_PART')
#     # if ('REPRESENTATION_CONTEXT' in entity_types
#     #     and any('TOP_LEVEL_ASSEMBLY_PART' in arg for arg in entity_args[entity_types.index('REPRESENTATION_CONTEXT')])):
#     #     return split_complex_types(entity_types,
#     #                            entity_args,
#     #                            ['REPRESENTATION_CONTEXT',
#     #                             'GEOMETRIC_REPRESENTATION_CONTEXT',
#     #                             'GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT',
#     #                             'GLOBAL_UNIT_ASSIGNED_CONTEXT'],
#     #                            'TOP_LEVEL_ASSEMBLY_PART')
    
#     print(entity_types)

#     return None, None


def parse_complex_type(complex_type_args: str):
    entities = split_complex_type_entities(complex_type_args)
    complex_types = []
    full_args = []
    for e in entities:
        m = re.match(r"(\w*)\s*\((.*)\)", e)
        if m:
            entity_type = m.group(1)
            raw_args = m.group(2)
            args = split_arguments(raw_args)
            complex_types.append({
                'type': entity_type,
                'arg_offset': len(full_args),
                'n_args': len(args)
            })
            full_args += args
        else:
            print('no parse', e)

    return complex_types, full_args
