import os
import json

from bottle import static_file, view, run, route, template, request, redirect

from utilities import get_documents
from foxtest.Converter import *
from foxtest.QuizMap import *


@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static/')


@route('/')
def home():
    try:
        single_documents, multiple_documents = get_documents()
    except NotADirectoryError as e:
        return str(e)
    return template('home.html', {'single_docs': single_documents, 'multiple_docs': multiple_documents})


@route('/<folder:re:[ms]>/<name>.doc')
def document(folder, name):
    dir = 'docs/single/' if folder == 's' else 'docs/multiple/'
    abs_dir = os.path.abspath(dir)
    map_json_path = os.path.join(abs_dir, name + '.map.json')

    info = None
    if os.path.exists(map_json_path):
        with open(map_json_path, 'r') as file:
            quiz_map = json.load(file, object_hook=decode_quiz_map)
        info = quiz_map.info

    return template('converter.html', {'name': name, 'folder': folder, 'info': info})


@route('/find/<folder:re:[ms]>/<name>.doc', method='POST')
def find(folder, name):
    dir = 'docs/single/' if folder == 's' else 'docs/multiple/'
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
    dir = 'docs/single/' if folder == 's' else 'docs/multiple/'
    abs_dir = os.path.abspath(dir)
    document_path = os.path.join(abs_dir, name + '.doc')
    map_json_path = os.path.join(abs_dir, name + '.map.json')
    if not os.path.exists(document_path):
        return f'Ошибка: документ не найден. Путь: {document_path}'
    with open(map_json_path, 'r') as file:
        quiz_map = json.load(file, object_hook=decode_quiz_map)
    word, doc = open_document(document_path)
    quizes = convert(doc, quiz_map)
    return {'quizes': quizes}


run(host='localhost', port=8080, debug=True, reloader=True)
