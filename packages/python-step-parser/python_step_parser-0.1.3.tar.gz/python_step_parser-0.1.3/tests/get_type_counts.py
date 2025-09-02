from src.python_step_parser.step_parser import StepParser

def get_type_counts(step_file: str):
    parser = StepParser(step_file)
    parser.parse()

    entity_counts = parser.query("""
                                 SELECT COUNT(*), type
                                 FROM step_entities
                                 GROUP BY type
                                 ORDER BY type""")

    for p in entity_counts:
        print('{: <8} {}'.format(p[0], p[1]))