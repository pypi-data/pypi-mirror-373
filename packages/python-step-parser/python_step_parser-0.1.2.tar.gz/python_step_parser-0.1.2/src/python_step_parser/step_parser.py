import sqlite3
import os
from typing import Dict, List, Any

from .parsers.cache_logic import load_entities, load_complex_items, load_list_text, load_args_and_parents
from .parsers.complex_item_dto import ComplexItemDTO
from .parsers.helpers import parse_arg_value, get_all_complex_args
from .parsers.parser import parse_and_store_step

class StepParser():
    step_file: str
    db_file: str
    conn: sqlite3.Connection
    connected: bool = False

    entity_type_cache: Dict[int, str] = {}
    complex_item_cache: Dict[int, List[ComplexItemDTO]] = {}
    arg_cache: Dict[int, List[Any]] = {}
    list_text_cache: Dict[int, List[Any]] = {}
    parent_ref_cache = {}
    cache_loaded: bool = False

    def __init__(self, step_file: str):
        self.step_file = step_file
        self.db_file = f'{self.step_file}.db'
        pass

    def parse(self, override=False, filename=None):
        if filename is not None:
            self.db_file = filename
        if not os.path.isfile(self.step_file):
            raise Exception('Could not find file {}'.format(self.step_file))
        if os.path.isfile(self.db_file) and override:
            os.remove(self.db_file)
        if not os.path.isfile(self.db_file):
            parse_and_store_step(f'{self.step_file}', f'{self.step_file}.db')

    def __connect(self):
        if not self.connected:
            self.conn = sqlite3.connect(self.db_file)
            self.connected = True

    def __get_cursor(self):
        self.__connect()
        return self.conn.cursor()

    def query(self, query_str: str) -> List[List[Any]]:
        cursor = self.__get_cursor()
        cursor.execute(query_str)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_arguments(self, entity_id: int):
        if entity_id in self.arg_cache:
            return self.arg_cache[entity_id]
        if self.cache_loaded:
            raise Exception("Fatal arg_cache miss for entity {}".format(entity_id))
        
        print(f'cache miss {entity_id} ({type(entity_id)})')

        cursor = self.__get_cursor()
        cursor.execute(f"""
                    SELECT id, value_type, value_text
                    FROM step_arguments
                    WHERE entity_id={entity_id}
                    ORDER BY arg_index;""")
        args = [
            parse_arg_value(row[1].strip(), row[2].strip())
            for row
            in cursor.fetchall()
        ]
        self.arg_cache[entity_id] = args
        return args
    
    def get_complex_items(self, entity_id: int, fail=True) -> List[ComplexItemDTO]:
        if entity_id in self.complex_item_cache:
            return self.complex_item_cache[entity_id]
        if self.cache_loaded:
            if fail:
                raise Exception("Fatal complex_item_cache miss for entity {}".format(entity_id))
            else:
                return []
        
        cursor = self.__get_cursor()
        cursor.execute(f"""
                    SELECT entity_id, item_index, type, step_arguments_offset, n_args
                    FROM step_complex_items
                    WHERE entity_id={entity_id}
                    ORDER BY item_index;""")
        items = [
            ComplexItemDTO(row[2], int(row[3]), int(row[4]))
            for row
            in cursor.fetchall()
        ]

        self.complex_item_cache[entity_id] = items
        return items

    def get_complex_or_base_arguments(self, entity_id: int, complex_types: List[str]):
        args = self.get_arguments(entity_id)
        complex_items = self.get_complex_items(entity_id, False)
        if len(complex_items) > 0:
            return get_all_complex_args(args,
                                             complex_items,
                                             complex_types)
        return args

    def get_list_text(self, argument_id: int, depth:int=0):
        if argument_id in self.list_text_cache:
            return self.list_text_cache[argument_id]
        
        if self.cache_loaded:
            raise Exception("Fatal list_text_cache miss for argument {}".format(argument_id))
        
        cursor = self.__get_cursor()
        cursor.execute(f"""
                    SELECT value_type, value_text
                    FROM step_list_items
                    WHERE argument_id={argument_id}
                    ORDER BY item_index;""")
        val = [
            parse_arg_value(row[0].strip(), row[1].strip() if row[1] is not None else None)
            for row
            in cursor.fetchall()
        ]
        self.list_text_cache[argument_id] = val
        return val
    
    def get_arg_value_with_list_traversal(self, argument_id: int, value_type: str, value_text: str) -> Any:
        if value_type == 'list':
            return self.get_list_text(argument_id)
        return parse_arg_value(value_type, value_text)

    def get_entity_list(conn: sqlite3.Connection, type: str) -> List[int]:
        cursor = conn.cursor()
        cursor.execute(f"SELECT Id FROM step_entities WHERE type = '{type}';")
        return [int(row[0]) for row in cursor.fetchall()]

    def get_entity_type(self, id: int) -> str:
        if id in self.entity_type_cache:
            return self.entity_type_cache[id]
        if self.cache_loaded:
            raise Exception("Fatal cache miss")
        
        cursor = self.__get_cursor()
        cursor.execute(f"SELECT type FROM step_entities WHERE Id = '{id}';")
        val = [str(row[0]).upper() for row in cursor.fetchall()][0]
        self.entity_type_cache[id] = val
        return val

    def get_representation_contexts(self) -> List[int]:
        cursor = self.__get_cursor()

        cursor.execute(f"""
                    SELECT id
                    FROM step_entities
                    WHERE type IN ('GEOMETRIC_REPRESENTATION_CONTEXT')
                    ORDER BY id""")
        
        simple_entities = [int(row[0]) for row in cursor.fetchall()]
        
        cursor.execute(f"""
                    SELECT distinct entity_id
                    FROM step_complex_items
                    WHERE type = 'GEOMETRIC_REPRESENTATION_CONTEXT'
                    ORDER BY entity_id""")
        
        complex_entities = [int(row[0]) for row in cursor.fetchall()]
        
        cursor.close()
        
        return simple_entities + complex_entities

    def get_parents(self, id: int) -> List[int]:
        return [] if id not in self.parent_ref_cache else self.parent_ref_cache[id]

    def load_cache(self) -> None:
        print('[*] Loading data cache')

        cursor = self.__get_cursor()

        # Load entities
        self.entity_type_cache = load_entities(cursor)
        print(f'[*] Loaded {len(self.entity_type_cache)} step_entities into memory cache')
        
        # Load complex items
        self.complex_item_cache = load_complex_items(cursor)
        print(f'[*] Loaded {len(self.complex_item_cache)} step_complex_items into memory cache')

        # Load step list items
        self.list_text_cache = load_list_text(cursor)
        print(f'[*] Loaded {len(self.list_text_cache)} step_list_items into memory cache')

        # Load arguments
        self.arg_cache, self.parent_ref_cache = load_args_and_parents(cursor, self.get_arg_value_with_list_traversal)
        print(f'[*] Loaded {len(self.arg_cache)} step_arguments into memory cache')

        cursor.close()

        self.cache_loaded = True