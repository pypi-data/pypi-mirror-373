from subprocess import run
import os

def init(sql_url: str, path: str = 'src/alembic', tables_folder: str = 'src/tables') -> None:
    run(['alembic', 'init', path])
    env_file = path + '/env.py'
    add_string_to_file(env_file, 'from eaasy.domain.database import Base', 0)
    add_string_to_file(env_file, f'from {tables_folder.replace('/', '.')} import *', 1)
    replace_string_in_file(env_file, 'target_metadata = None', 'target_metadata = Base.metadata')
    replace_string_in_file('alembic.ini', 'sqlalchemy.url = driver://user:pass@localhost/dbname', f'sqlalchemy.url = {sql_url}')

    os.makedirs(tables_folder, exist_ok=True)
    with open(tables_folder + '/__init__.py', 'w') as file:
        file.write('# Import here your tables and add them in __all__ property\n\n__all__ = []')

def add_string_to_file(file_path: str, string_to_add: str, line_number: int):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    index = max(0, min(line_number - 1, len(lines)))
    lines.insert(index, string_to_add + '\n')
    with open(file_path, 'w') as file:
        file.writelines(lines)

def replace_string_in_file(file_path: str, string_to_replace: str, new_string: str):
    with open(file_path, 'r') as file:
        filedata = file.read()
    newdata = filedata.replace(string_to_replace, new_string)
    with open(file_path, 'w') as file:
        file.write(newdata)
