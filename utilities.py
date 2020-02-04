from os import listdir
from os.path import isfile, join, exists, splitext

main_dir = 'docs'
single_dir = 'docs/singer'
multiple_dir = 'docs/mullein'


def converted(name, mode) -> bool:
    dir = single_dir if mode == 1 else multiple_dir
    json_name = name + '.json'
    return exists(join(dir, json_name))


def get_documents() -> tuple:
    if not exists(main_dir):
        raise NotADirectoryError(f'Папка <b>{main_dir}</b> не найден')
    if not exists(single_dir):
        raise NotADirectoryError(f'Папка <b>{single_dir}</b> не найден')
    if not exists(multiple_dir):
        raise NotADirectoryError(f'Папка <b>{multiple_dir}</b> не найден')

    single_docs = [f for f in listdir(single_dir) if isfile(join(single_dir, f)) and splitext(f)[1] == '.doc']
    single_documents = []
    for doc in single_docs:
        json_name = splitext(doc)[0] + '.json'
        d = {
            'name': doc,
            'converted': exists(join(single_dir, json_name)),
            'folder': 's'
        }
        single_documents.append(d)

    multiple_docs = [f for f in listdir(multiple_dir) if isfile(join(multiple_dir, f)) and splitext(f)[1] == '.doc']
    multiple_documents = []
    for doc in multiple_docs:
        json_name = splitext(doc)[0] + '.json'
        d = {
            'name': doc,
            'converted': exists(join(multiple_dir, json_name)),
            'folder': 'm'
        }
        multiple_documents.append(d)

    return single_documents, multiple_documents