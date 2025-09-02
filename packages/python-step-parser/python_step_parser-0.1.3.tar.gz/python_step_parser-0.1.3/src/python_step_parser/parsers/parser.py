import re
from typing import List, Dict, Union
from .complex_type_parsers import parse_complex_type
from .helpers import split_arguments
from .db_helpers import init_db, save_entities_to_db

# --- STEP Parsing Functions ---

def parse_step_file(filepath: str) -> Dict[int, Dict]:
    """Parses STEP and returns entities."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    data_match = re.search(r"DATA;(.*?)ENDSEC;", content, re.DOTALL | re.IGNORECASE)
    if not data_match:
        raise ValueError("No DATA section found in STEP file.")

    data = data_match.group(1).strip()
    entities = {}

    lines = data.splitlines()
    n = len(lines)

    for i in range(0, n):
        # if i % 1000 == 0:
        #     print(f'parsed line {i}')
        line = lines[i]

        # Handle multi-line items
        line_parts = []
        if ';' not in line:
            line_parts.append(lines[i])
        while ';' not in lines[i]:
            line_parts.append(lines[i + 1])
            i += 1
        if len(line_parts) > 0:
            line = ' '.join(line_parts)

        line = line.strip().rstrip(';')
        if not line.startswith('#'):
            continue
        m = re.match(r"#(\d+)\s*=\s*(\w*)\s*\((.*)\)", line)
        if m:
            entity_id = int(m.group(1))
            entity_type = m.group(2)
            raw_args = m.group(3)
            
            if entity_type.strip() == '':
                entity_type = 'COMPLEX'
                complex_items, args = parse_complex_type(raw_args)
                # if entity_type is None:
                #     print('[!] Failed to parse:', line)
                #     continue
            else:
                complex_items = None
                args = split_arguments(raw_args)
            entities[entity_id] = {
                'type': entity_type,
                'args': args,
                'complex_items': complex_items
            }
    return entities


# --- Main Execution ---

def parse_and_store_step(step_file: str, db_file: str):
    entities = parse_step_file(step_file)
    print('parsed step file')
    conn = init_db(db_file)
    print('db initialized')
    save_entities_to_db(conn, entities)
    conn.close()
    print(f"STEP file parsed and saved to '{db_file}'.")
