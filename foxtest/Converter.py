import os
import re
import base64
import sys
from io import BytesIO

import win32com.client
from PIL import Image

from .WordConstants import *
from .QuizMap import QuizMap, QuestionMap


def open_document(path: str) -> tuple:
    path = path if os.path.isabs(path) else os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Ошибка: {os.path.basename(path)} не найден или не является файлом. '
                                f'Полный путь: {path}')
    if not os.path.splitext(path)[1] == '.doc':
        raise TypeError(f'Формат файла не является .doc')

    word = win32com.client.Dispatch('Word.Application')
    word.Visible = True
    doc = word.Documents.Open(path)
    return word, doc


def paragraph_to_html(doc, para):
    rng = doc.Range(para.Range.Start, para.Range.End - 1)
    rng.Find.Text = ''
    rng.Find.Font.Superscript = True
    while rng.Find.Execute():
        rng.InsertBefore('<sup>')
        rng.InsertAfter('</sup>')
        rng.Font.Superscript = False
        rng = doc.Range(rng.End, para.Range.End - 1)

    rng = doc.Range(para.Range.Start, para.Range.End - 1)
    rng.Find.Font.Subscript = True
    while rng.Find.Execute():
        rng.InsertBefore('<sub>')
        rng.InsertAfter('</sub>')
        rng.Font.Subscript = False
        rng = doc.Range(rng.End, para.Range.End - 1)

    rng = doc.Range(para.Range.Start, para.Range.End - 1)
    rng.Find.Font.Underline = True
    while rng.Find.Execute():
        rng.InsertBefore('<u>')
        rng.InsertAfter('</u>')
        rng.Font.Underline = False
        rng = doc.Range(rng.End, para.Range.End - 1)

    rng = doc.Range(para.Range.Start, para.Range.End - 1)
    rng.Find.Font.Italic = True
    while rng.Find.Execute():
        rng.InsertBefore('<i>')
        rng.InsertAfter('</i>')
        rng.Font.Italic = False
        rng = doc.Range(rng.End, para.Range.End - 1)

    para.Range.Find.Execute(FindText='\\n',
                             MatchCase=False,
                             MatchWholeWord=False,
                             MatchWildcards=False,
                             MatchSoundsLike=False,
                             MatchAllWordForms=False,
                             Forward=True,
                             Wrap=WdFindWrap.wdFindContinue,
                             Format=False,
                             ReplaceWith='<br/>',
                             Replace=WdReplace.wdReplaceAll)

    shapeScale = 4
    img_temp = '<img align="Middle" src="data:image/png;base64,{0}" />'
    for shape in para.Range.InlineShapes:
        wmfim = Image.open(BytesIO(shape.Range.EnhMetaFileBits))
        wmfim = wmfim.resize(map(lambda heightwidth: heightwidth // shapeScale, wmfim.size))
        bimage = BytesIO()
        wmfim.save(bimage, format='png')
        img_str = base64.b64encode(bimage.getvalue())
        shape.Range.Text = img_temp.format(img_str.decode('ascii'))

    return para.Range.Text.strip()


def pre_find(func):
    def wrapper(doc, choices_len):
        symbols = (('^13', '^p'),
                   ('^l', '^p'))
        for from_, to_ in symbols:
            doc.Range().Find.Execute(FindText=from_,
                                     MatchCase=False,
                                     MatchWholeWord=False,
                                     MatchWildcards=False,
                                     MatchSoundsLike=False,
                                     MatchAllWordForms=False,
                                     Forward=True,
                                     Wrap=WdFindWrap.wdFindContinue,
                                     Format=False,
                                     ReplaceWith=to_,
                                     Replace=WdReplace.wdReplaceAll)
        doc.Save()

        if type(choices_len) is not int:
            try:
                choices_len = int(choices_len)
            except Exception as e:
                raise e

        return func(doc, choices_len)
    return wrapper


@pre_find
def find_questions_single(doc, choices_len=5) -> QuizMap:
    choices_count = choices_len
    question_pattern = re.compile('(^ ?\d{1,3})( ?\. *)')
    choice_pattern = re.compile('^ ?[A-ZА-Я]{1} ?\)')

    quiz_map = QuizMap()
    quiz_map.questions = []
    quiz_map.error_questions = []

    for i, para in enumerate(doc.Paragraphs, 1):
        if question_pattern.match(para.Range.Text):
            # print('- question_pattern matches -')
            empty, number, dot, text = question_pattern.split(para.Range.Text)

            question_map = QuestionMap()
            question_map.real_number = int(number)
            question_map.paragraph_id = i

            question_map.answers = []
            question_map.fake_answers = []

            if choice_pattern.match(doc.Paragraphs(i + 1).Range.Text):
                pre_count = doc.Paragraphs(i + 1).Range.Text.index(")") + 1
                question_map.answers.append(
                    {"paragraph_id": i + 1,
                     "pre_count": pre_count}
                )

            for j in range(2, choices_count + 1):
                if choice_pattern.match(doc.Paragraphs(i + j).Range.Text):
                    pre_count = doc.Paragraphs(i + j).Range.Text.index(")") + 1
                    question_map.fake_answers.append(
                        {"paragraph_id": i + j,
                         "pre_count": pre_count}
                    )

            ans_len = len(question_map.answers) + len(question_map.fake_answers)
            if ans_len == choices_count:
                quiz_map.questions.append(question_map)
            else:
                quiz_map.error_questions.append(question_map)
    return quiz_map


@pre_find
def find_questions_multiple(doc, choices_len=6) -> QuizMap:
    choices_count = choices_len
    question_pattern = re.compile('(^ ?\d{1,3})( ?\. *)')
    choice_pattern = re.compile('^[A-ZА-ЯӘҢҒҮҰҚӨҺ] ?\) ?\[(\d\.\d)]')

    quiz_map = QuizMap()
    quiz_map.questions = []
    quiz_map.error_questions = []

    for i, para in enumerate(doc.Paragraphs, 1):
        if question_pattern.match(para.Range.Text):
            empty, number, dot, text = question_pattern.split(para.Range.Text)

            question_map = QuestionMap()
            question_map.real_number = int(number)
            question_map.paragraph_id = i
            question_map.answers = []
            question_map.fake_answers = []

            for j in range(1, choices_count + 1):
                id = i + j
                if choice_pattern.match(doc.Paragraphs(id).Range.Text):
                    empty, number, *_ = choice_pattern.split(doc.Paragraphs(id).Range.Text)
                    pre_count = doc.Paragraphs(id).Range.Text.index("]") + 1
                    number = float(number)
                    if number > 0:
                        question_map.answers.append(
                            {"paragraph_id": id,
                             "pre_count": pre_count}
                        )
                    else:
                        question_map.fake_answers.append(
                            {"paragraph_id": id,
                             "pre_count": pre_count}
                        )

            ans_len = len(question_map.answers) + len(question_map.fake_answers)
            if ans_len == choices_count:
                quiz_map.questions.append(question_map)
            else:
                quiz_map.error_questions.append(question_map)
    return quiz_map


def pre_convert(func):
    def wrapper(doc, quiz_map):
        symbols = (('^u61477', '%'),
                   ('^u61513', 'I'),
                   ('^u61472', ' '),
                   ('&', '&amp;'),
                   ('<', '&lt;'),
                   ('>', '&gt;'),
                   ('"', '&quot;'),
                   ('\'', '&#39;'))
        for code, symbol in symbols:
            doc.Range().Find.Execute(FindText=code,
                                     MatchCase=False,
                                     MatchWholeWord=False,
                                     MatchWildcards=False,
                                     MatchSoundsLike=False,
                                     MatchAllWordForms=False,
                                     Forward=True,
                                     Wrap=WdFindWrap.wdFindContinue,
                                     Format=False,
                                     ReplaceWith=symbol,
                                     Replace=WdReplace.wdReplaceAll)
        return func(doc, quiz_map)
    return wrapper


@pre_convert
def convert(doc, quiz_map: QuizMap) -> list:
    quizes = list()
    for id, question_map in enumerate(quiz_map.questions, 1):
        sys.stdout.write('\rConverting... {already}/{all}'.format(already=question_map.real_number, all=quiz_map.max))
        quiz = dict()
        quiz['id'] = id
        quiz['number'] = question_map.real_number
        quiz['question'] = paragraph_to_html(doc, doc.Paragraphs(question_map.paragraph_id))

        quiz['answers'] = list()
        for answer in question_map.answers:
            full_text = paragraph_to_html(doc, doc.Paragraphs(answer['paragraph_id']))
            pre = full_text[:answer['pre_count']].strip()
            text = full_text[answer['pre_count']:].strip()
            quiz['answers'].append([pre, text])

        quiz['fake_answers'] = list()
        for fake_answer in question_map.fake_answers:
            full_text = paragraph_to_html(doc, doc.Paragraphs(fake_answer['paragraph_id']))
            pre = full_text[:fake_answer['pre_count']].strip()
            text = full_text[fake_answer['pre_count']:].strip()
            quiz['fake_answers'].append([pre, text])
        quizes.append(quiz)
    print()
    return quizes
