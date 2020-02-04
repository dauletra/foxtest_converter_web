from typing import List
import json


class QuestionMap:
    real_number: int = None
    paragraph_id: int = None
    answers: list = None
    fake_answers: list = None

    @staticmethod
    def create(real_number, paragraph_id, answers, fake_answers):
        question_map = QuestionMap()
        question_map.real_number = real_number
        question_map.paragraph_id = paragraph_id
        question_map.answers = answers
        question_map.fake_answers = fake_answers
        return question_map


class QuizMap:
    questions: List[QuestionMap] = None
    error_questions: List[QuestionMap] = None

    @staticmethod
    def create(questions, error_questions):
        quizmap = QuizMap()
        quizmap.questions, quizmap.error_questions = [], []
        for question in questions:
            quizmap.questions.append(QuestionMap.create(**question))
        for error_question in error_questions:
            quizmap.error_questions.append(QuestionMap.create(**error_question))
        return quizmap

    @property
    def info(self):
        a = ('Вопросы', f'{self.min}-{self.max}')
        b = ('Количество', str(self.count))
        c = ('Не найдено', ', '.join([str(num) for num in self.missed_numbers]))
        d = ('С ошибками', ', '.join([str(num) for num in self.error_numbers]))
        return a, b, c, d

    @property
    def max(self):
        return max([question.real_number for question in self.questions])

    @property
    def min(self):
        return min([question.real_number for question in self.questions])

    @property
    def count(self):
        return len(self.questions)

    @property
    def missed_numbers(self, only_missed=True):
        missed_numbers = []
        real_numbers = [question.real_number for question in self.questions]
        for i in range(min(real_numbers), max(real_numbers)):
            if i not in real_numbers:
                missed_numbers.append(i)
        if only_missed:
            return [missed_number for missed_number in missed_numbers if missed_number not in self.error_numbers]
        return missed_numbers

    @property
    def error_numbers(self):
        return [error_question.real_number for error_question in self.error_questions]


class QuizMapEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuizMap):
            questions = [{
                'real_number': question.real_number,
                'paragraph_id': question.paragraph_id,
                'answers': question.answers,
                'fake_answers': question.fake_answers} for question in obj.questions]
            error_questions = [{
                'real_number': error_question.real_number,
                'paragraph_id': error_question.paragraph_id,
                'answers': error_question.answers,
                'fake_answers': error_question.fake_answers} for error_question in obj.error_questions]
            return { 'questions': questions, 'error_questions': error_questions }


def decode_quiz_map(dic):
    if dic.get('questions') or dic.get('error_questions'):
        return QuizMap.create(dic['questions'], dic['error_questions'])
    else:
        return dic