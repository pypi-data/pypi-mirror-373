import sqlite3
from typing import List, Any, Dict, Tuple, Callable
from .complex_item_dto import ComplexItemDTO
from .helpers import parse_arg_value

def load_entities(cursor: sqlite3.Cursor) -> Dict[int, str]:
    """
    load entities from data file into dictionary in [key, type] format
    """
    entities_dict: Dict[int, str] = {}
    
    cursor.execute(f"SELECT Id, type FROM step_entities;")

    for row in cursor.fetchall():
        entities_dict[int(row[0])] = str(row[1]).upper()

    return entities_dict

def load_complex_items(cursor: sqlite3.Cursor) -> Dict[int, List[ComplexItemDTO]]:
    """
    """
    complex_items_dict: Dict[int, List[ComplexItemDTO]] = {}
    
    cursor.execute(f"""
                    SELECT entity_id, item_index, type, step_arguments_offset, n_args
                    FROM step_complex_items
                    ORDER BY entity_id, item_index;""")
    
    for row in cursor.fetchall():
        entity_id = int(row[0])
        if entity_id not in complex_items_dict:
            complex_items_dict[entity_id] = []
        complex_items_dict[entity_id].append(ComplexItemDTO(row[2], int(row[3]), int(row[4])))

    return complex_items_dict

def load_list_text(cursor: sqlite3.Cursor) -> Dict[int, List[Any]]:
    """
    """
    list_text_dict: Dict[int, List[Any]] = {}
    
    cursor.execute(f"""
                    SELECT argument_id, value_type, value_text
                    FROM step_list_items
                    ORDER BY argument_id, item_index;""")
    
    for row in cursor.fetchall():
        argument_id = int(row[0])
        if argument_id not in list_text_dict:
            list_text_dict[argument_id] = []
        list_text_dict[argument_id].append(parse_arg_value(row[1].strip(), row[2].strip()))

    return list_text_dict

def load_args_and_parents(cursor: sqlite3.Cursor, parse_arg: Callable[[int, str, str], Any]) -> Tuple[Dict[int, List[Any]], Dict[int, List[int]]]:
    """
    """
    args_dict: Dict[int, List[Any]] = {}
    parent_ref_dict: Dict[int, List[int]] = {}
    
    cursor.execute(f"""
                    SELECT entity_id, id, value_type, value_text
                    FROM step_arguments
                    ORDER BY entity_id, arg_index;""")
    
    for row in cursor.fetchall():
        entity_id = int(row[0])
        if entity_id not in args_dict:
            args_dict[entity_id] = []
        value_type = str(row[2]).strip()
        value_text = str(row[3]).strip() if row[3] is not None else None
        args_dict[entity_id].append(parse_arg(int(row[1]), value_type, value_text))
        
        if value_type.lower() == 'reference':
            ref_id = int(value_text)
            if ref_id not in parent_ref_dict:
                parent_ref_dict[ref_id] = []
            parent_ref_dict[ref_id].append(entity_id)

    return args_dict, parent_ref_dict
