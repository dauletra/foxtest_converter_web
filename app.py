import os
import json
from time import time

from bottle import run, route, static_file, template, view, request, redirect

from foxtest.Converter import *
from foxtest.QuizMap import *
from foxtest.Subject import *


@route('/')
def home():
    main_dir = 'docs'
    quiz_categories = ['singer', 'mullein']
    folders = []
    
    for dir in quiz_categories:
        abs_path = os.path.abspath(os.path.join(main_dir, dir))
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
            'name': dir,
            'initial': dir[0],
            'documents': documents
        })

    return template('home.html', {'folders': folders})


@route('/<folder:re:[ms]>/<name>.doc')
def document(folder, name):
    dir = 'docs/singer/' if folder == 's' else 'docs/mullein/'
    abs_dir = os.path.abspath(dir)
    # if quiz converted then redirect to /quiz/name.json
    quiz_json_path = os.path.join(abs_dir, name + '.json')
    if os.path.exists(quiz_json_path):
        return redirect('/' + folder + '/' + name + '.json')

    map_json_path = os.path.join(abs_dir, name + '.map.json')
    info = None
    if os.path.exists(map_json_path):
        with open(map_json_path, 'r') as file:
            quiz_map = json.load(file, object_hook=decode_quiz_map)
        info = quiz_map.info

    return template('converter.html', {'name': name, 'folder': folder, 'info': info})


@route('/<folder:re:[ms]>/<name>.json')
def quiz(folder, name):
    dir = 'docs/singer/' if folder == 's' else 'docs/multiple'
    abs_dir = os.path.abspath(dir)
    quiz_json_path = os.path.join(abs_dir, name + '.json')
    if not os.path.exists(quiz_json_path):
        return f'Ошибка. Тест с названием {name}.json не найден'
    with open(quiz_json_path, 'r', encoding='utf-8') as file:
        subject = json.load(file, object_hook=decode_subject)
    return template('quiz.html', {'name': name, 'subject': subject.get_dict()})


@route('/find/<folder:re:[ms]>/<name>.doc', method='POST')
def find(folder, name):
    dir = 'docs/singer/' if folder == 's' else 'docs/mullein/'
    abs_dir = os.path.abspath(dir)
    document_path = os.path.join(abs_dir, name + '.doc')
    if not os.path.exists(document_path):
        return f'Ошибка: документ не найден. Путь: {document_path}'
    word, doc = open_document(document_path)
    find = {'m': find_questions_multiple, 's': find_questions_single}
    quiz_map = find[folder](doc)
    json_path = os.path.join(abs_dir, name + '.map.json')
    with open(json_path, 'w') as file:
        json.dump(quiz_map, file, cls=QuizMapEncoder)
    return redirect('/'+folder+'/'+name+'.doc')


@route('/convert/<folder:re:[ms]>/<name>.doc', method='POST')
def convert_(folder, name):
    dir = 'docs/singer/' if folder == 's' else 'docs/mullein/'
    abs_dir = os.path.abspath(dir)
    document_path = os.path.join(abs_dir, name + '.doc')
    map_json_path = os.path.join(abs_dir, name + '.map.json')
    quiz_json_path = os.path.join(abs_dir, name + '.json')
    mode = 1 if folder == 's' else 2
    if not os.path.exists(document_path):
        return f'Ошибка: документ не найден. Путь: {document_path}'
    if not os.path.exists(map_json_path):
        return f'Ошибка: карта документа не найден. Путь: {map_json_path}'
    with open(map_json_path, 'r') as file:
        quiz_map = json.load(file, object_hook=decode_quiz_map)
    word, doc = open_document(document_path)
    quizes = convert(doc, quiz_map)

    subject = Subject.create(mode=mode, quizes=quizes)
    with open(quiz_json_path, 'w') as file:
        json.dump(subject, file, cls=SubjectEncoder)
    return redirect('/'+folder+'/'+name+'.doc')


@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static/')


run(host='localhost', port=8080, debug=True, reloader=True)
