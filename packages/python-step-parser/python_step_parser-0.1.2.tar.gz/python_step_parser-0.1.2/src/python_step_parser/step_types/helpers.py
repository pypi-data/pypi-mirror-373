def clean_display(val, padding='    '):
    if val is None:
        return 'n/a'
    return str(val).replace('\n', f'\n{padding}').strip()

def clean_display_doublelist(vals, padding='    '):
    if vals is None:
        return '[]'
    return f'''[
    {padding}{f'\n{padding}'.join([
        clean_display_list(v) for v in vals
    ]).replace('\n', f'\n{padding}').strip()}
{padding}]'''

def clean_display_list(vals, padding='    '):
    if vals is None:
        return '[]'
    return f'''[
    {padding}{f'\n{padding}'.join([
        clean_display(v) for v in vals
    ]).replace('\n', f'\n{padding}').strip()}
{padding}]'''
