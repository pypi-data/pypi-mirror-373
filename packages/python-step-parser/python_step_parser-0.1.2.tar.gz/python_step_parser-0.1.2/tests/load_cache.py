from src.python_step_parser.step_parser import StepParser
import time

def get_type_counts(step_file: str):
    parser = StepParser(step_file)
    parser.parse()

    print('loading cache')
    t = time.time()
    parser.load_cache()
    print(f'loaded cache in {round((time.time() - t) * 1000, 0)}')