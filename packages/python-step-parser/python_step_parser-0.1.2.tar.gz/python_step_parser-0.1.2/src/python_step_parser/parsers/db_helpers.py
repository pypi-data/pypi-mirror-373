from .helpers import split_arguments, classify_arg
import sqlite3
from typing import List, Dict, Union

# --- SQLite Setup ---

def init_db(db_file: str):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create tables
    c.execute("""
        CREATE TABLE IF NOT EXISTS step_entities (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS step_complex_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            item_index INTEGER NOT NULL,
            type TEXT NOT NULL,
            step_arguments_offset INTEGER NOT NULL,
            n_args INTEGER NOT NULL,
            FOREIGN KEY(entity_id) REFERENCES step_entities(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS step_arguments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            arg_index INTEGER NOT NULL,
            value_type TEXT NOT NULL,
            value_text TEXT,
            FOREIGN KEY(entity_id) REFERENCES step_entities(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS step_list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            argument_id INTEGER NOT NULL,
            item_index INTEGER NOT NULL,
            value_type TEXT NOT NULL,
            value_text TEXT,
            FOREIGN KEY(argument_id) REFERENCES step_arguments(id)
        );
    """)
    conn.commit()
    return conn

# --- DB Insertion Logic ---

def insert_entity(conn, entity_id: int, entity_type: str):
    cursor = conn.cursor()
    # Insert or replace the entity
    cursor.execute("""
        INSERT INTO step_entities (id, type)
        VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET type=excluded.type;
    """, (entity_id, entity_type))

def insert_complex_item(conn, entity_id: int, index: int, complex_type: str, arg_offset: int, n_args: int):
    cursor = conn.cursor()
    # Insert or replace the entity
    cursor.execute("""
        INSERT INTO step_complex_items (entity_id, item_index, type, step_arguments_offset, n_args)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET type=excluded.type;
    """, (entity_id, index, complex_type, arg_offset, n_args))

def insert_argument(conn, entity_id: int, index: int, value_type: str, value_text: Union[str, None]) -> int:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO step_arguments (entity_id, arg_index, value_type, value_text)
        VALUES (?, ?, ?, ?);
    """, (entity_id, index, value_type, value_text))
    return cursor.lastrowid

def insert_list_items(conn, argument_id: int, list_string: str):
    cursor = conn.cursor()
    list_items = split_arguments(list_string[1:-1])  # strip parentheses
    for i, item in enumerate(list_items):
        vtype, vtext = classify_arg(item)
        cursor.execute("""
            INSERT INTO step_list_items (argument_id, item_index, value_type, value_text)
            VALUES (?, ?, ?, ?);
        """, (argument_id, i, vtype, vtext))

def save_entities_to_db(conn, entities: Dict[int, Dict]):
    for entity_id, data in entities.items():
        entity_type = data['type']
        insert_entity(conn, entity_id, entity_type)

        for i, raw_arg in enumerate(data['args']):
            value_type, value_text = classify_arg(raw_arg)
            arg_id = insert_argument(conn, entity_id, i, value_type, value_text)
            if value_type == 'list':
                insert_list_items(conn, arg_id, value_text)

        if 'complex_items' in data and data['complex_items'] is not None:
            for i, complex_item in enumerate(data['complex_items']):
                insert_complex_item(conn, entity_id, i, complex_item['type'], complex_item['arg_offset'], complex_item['n_args'])

    conn.commit()