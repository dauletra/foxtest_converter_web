import os
import json
from time import time
from datetime import datetime

from bottle import run, route, static_file, template, view, request, redirect

from foxtest.Converter import *
from foxtest.QuizMap import *
from foxtest.Subject import *


main_dir = 'docs'
quiz_categories = [
    {
        'name': 'multiple',
        'initial': 'm',
        'mode': 2
    },
    {
        'name': 'single',
        'initial': 's',
        'mode': 1
    }
]


@route('/')
def home():
    folders = []
    for dir in quiz_categories:
        abs_path = os.path.abspath(os.path.join(main_dir, dir['name']))
        if not os.path.exists(abs_path):
            raise NotADirectoryError(f'Папка {abs_path} не существует')
        mod_time = os.path.getmtime(abs_path)
        document_names = [f for f in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, f)) and os.path.splitext(f)[1] == '.doc' and os.path.basename(f)[:2] != '~$']
        documents = []
        for document_name in document_names:
            quiz_json_name = os.path.splitext(document_name)[0] + '.json'
            map_json_name = os.path.splitext(document_name)[0] + '.map.json'
            status = 'Новый'
            status_number = 1
            if os.path.exists(os.path.join(abs_path, quiz_json_name)):
                status = 'Конвертирован'
                status_number = 5
            elif os.path.exists(os.path.join(abs_path, map_json_name)):
                status = 'Не ковертирован'
                status_number = 3
            document_mod_time = os.path.getmtime(os.path.join(abs_path, document_name))
            documents.append({
                'name': document_name,
                'status': status,
                'status_number': status_number,
                'mod_time': document_mod_time,
                'mod_time_readable': datetime.fromtimestamp(document_mod_time).strftime('%d-%m-%Y %H:%M')
            })
        sorted_documents = sorted(documents, key=lambda document: document['mod_time'], reverse=True)
        folders.append({
            'name': dir['name'],
            'initial': dir['initial'],
            'documents': sorted_documents,
            'mod_time': mod_time,
            'mod_time_readable': datetime.fromtimestamp(mod_time).strftime('%d-%m-%Y %H:%M')
        })
    sorted_folders = sorted(folders, key=lambda folder: folder['mod_time'], reverse=True)
    return template('home.html', {'folders': sorted_folders})


def document_paths(func):
    def wrapper(folder, name):
        folder_name = [dir for dir in quiz_categories if dir['initial'] == folder][0]['name']
        abs_dir = os.path.abspath(os.path.join(main_dir, folder_name))
        assert os.path.exists(abs_dir)

        document_path = os.path.join(abs_dir, name + '.doc')
        map_json_path = os.path.join(abs_dir, name + '.map.json')
        quiz_json_path = os.path.join(abs_dir, name + '.json')

        return func(folder, name, document_path, map_json_path, quiz_json_path)
    return wrapper


@route('/<folder:re:[ms]>/<name>.json')
@document_paths
def quiz(folder, name, document_path, map_json_path, quiz_json_path):
    if not os.path.exists(quiz_json_path):
        return f'Ошибка. Тест с названием {name}.json не найден'
    with open(quiz_json_path, 'r', encoding='utf-8') as file:
        subject = json.load(file, object_hook=decode_subject)
    return template('quiz.html', {'name': name, 'subject': subject.get_readable_dict()})


@route('/<folder:re:[ms]>/<name>.doc')
@document_paths
def document(folder, name, document_path, map_json_path, quiz_json_path):
    if os.path.exists(quiz_json_path):
        return redirect('/' + folder + '/' + name + '.json')

    info = None
    if os.path.exists(map_json_path):
        with open(map_json_path, 'r') as file:
            quiz_map = json.load(file, object_hook=decode_quiz_map)
        info = quiz_map.info

    find_link = '/find/' + folder + '/' + name + '.doc'
    convert_link = '/convert/' + folder + '/' + name + '.doc'
    return template('document.html', {'name': name, 'find_link': find_link, 'convert_link': convert_link, 'info': info})


@route('/find/<folder:re:[ms]>/<name>.doc', method='POST')
@document_paths
def find(folder, name, document_path, map_json_path, quiz_json_path):
    if not os.path.exists(document_path):
        return f'Ошибка: документ не найден. Путь: {document_path}'

    choices_len = request.forms['choices_len']

    word, doc = open_document(document_path)
    find = {'m': find_questions_multiple, 's': find_questions_single}
    quiz_map = find[folder](doc, choices_len=choices_len)
    with open(map_json_path, 'w') as file:
        json.dump(quiz_map, file, cls=QuizMapEncoder)
    return redirect('/'+folder+'/'+name+'.doc')


@route('/convert/<folder:re:[ms]>/<name>.doc', method='POST')
@document_paths
def convert_(folder, name, document_path, map_json_path, quiz_json_path):
    category = [category for category in quiz_categories if category['initial'] == folder][0]
    mode = category['mode']

    if not os.path.exists(document_path):
        return f'Ошибка: документ не найден. Путь: {document_path}'
    if not os.path.exists(map_json_path):
        return f'Ошибка: карта документа не найден. Путь: {map_json_path}'

    with open(map_json_path, 'r') as file:
        quiz_map = json.load(file, object_hook=decode_quiz_map)
    word, doc = open_document(document_path)

    quizes = convert(doc, quiz_map)
    quiz_name = request.forms.name
    quiz_comment = request.forms.comment

    subject = Subject.create(mode=mode, name=quiz_name, comment=quiz_comment, quizes=quizes)
    with open(quiz_json_path, 'w', encoding='utf8') as file:
        json.dump(subject, file, cls=SubjectEncoder, ensure_ascii=False)
    return redirect('/'+folder+'/'+name+'.doc')


@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static/')


run(host='localhost', port=8080, debug=True, reloader=True)
