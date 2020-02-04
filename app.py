import os
import json
from time import time

from bottle import run, route, static_file, template, view, request, redirect

from foxtest.Converter import *
from foxtest.QuizMap import *
from foxtest.Subject import *


main_dir = 'docs'
quiz_categories = [
    {
        'name': 'mullein',
        'initial': 'm',
        'mode': 2
    },
    {
        'name': 'singer',
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
        document_names = [f for f in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, f)) and os.path.splitext(f)[1] == '.doc']
        documents = []
        for document_name in document_names:
            test_name = os.path.splitext(document_name)[0] + '.json'
            converted = os.path.exists(os.path.join(abs_path, test_name))
            documents.append({
                'name': document_name,
                'converted': converted
            })
        folders.append({
            'name': dir['name'],
            'initial': dir['initial'],
            'documents': documents
        })

    return template('home.html', {'folders': folders})


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
    return template('quiz.html', {'name': name, 'subject': subject.get_dict()})


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
    word, doc = open_document(document_path)
    find = {'m': find_questions_multiple, 's': find_questions_single}
    quiz_map = find[folder](doc)
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
